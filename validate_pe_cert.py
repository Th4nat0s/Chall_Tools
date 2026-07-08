#!/usr/bin/env python3
"""
Validate certificates embedded in a signed PE Authenticode WIN_CERTIFICATE.

Checks performed:
- PE has IMAGE_DIRECTORY_ENTRY_SECURITY
- PKCS#7 certificate store can be parsed
- leaf certificate date validity
- leaf certificate has Code Signing EKU, when EKU extension exists
- optional OpenSSL chain validation against system trust or provided CA bundle
- optional OpenSSL PKCS#7 signature check

Note: this validates embedded certificates and PKCS#7 structure. It does not
fully recompute Microsoft Authenticode PE digest policy.
"""



import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import pefile
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import ExtendedKeyUsageOID
from cryptography.x509.oid import AuthorityInformationAccessOID


WIN_CERT_REVISION_2_0 = 0x0200
WIN_CERT_TYPE_PKCS_SIGNED_DATA = 0x0002
OID_SPC_INDIRECT_DATA = "1.3.6.1.4.1.311.2.1.4"
OID_DIGEST_ALGS = {
    "1.3.14.3.2.26": "sha1",
    "2.16.840.1.101.3.4.2.1": "sha256",
    "2.16.840.1.101.3.4.2.2": "sha384",
    "2.16.840.1.101.3.4.2.3": "sha512",
}


@dataclass
class WinCertificate:
    length: int
    revision: int
    cert_type: int
    blob: bytes


@dataclass
class Asn1Node:
    tag: int
    value: bytes
    children: list["Asn1Node"]


def decode_oid(data: bytes) -> str:
    if not data:
        return ""
    values = [data[0] // 40, data[0] % 40]
    acc = 0
    for byte in data[1:]:
        acc = (acc << 7) | (byte & 0x7F)
        if not byte & 0x80:
            values.append(acc)
            acc = 0
    return ".".join(str(value) for value in values)


def read_asn1_node(data: bytes, offset: int = 0) -> tuple[Asn1Node, int]:
    if offset + 2 > len(data):
        raise ValueError("ASN.1 tronqué")

    tag = data[offset]
    pos = offset + 1
    first_len = data[pos]
    pos += 1
    if first_len == 0x80:
        raise ValueError("ASN.1 BER indefinite length not supported")
    if first_len < 0x80:
        length = first_len
    else:
        len_len = first_len & 0x7F
        if len_len == 0 or pos + len_len > len(data):
            raise ValueError("ASN.1 invalid length")
        length = int.from_bytes(data[pos : pos + len_len], "big")
        pos += len_len

    end = pos + length
    if end > len(data):
        raise ValueError("ASN.1 length exceeds buffer")

    value = data[pos:end]
    children: list[Asn1Node] = []
    if tag & 0x20:
        child_pos = 0
        while child_pos < len(value):
            child, child_pos = read_asn1_node(value, child_pos)
            children.append(child)
    return Asn1Node(tag, value, children), end


def walk_asn1(node: Asn1Node):
    yield node
    for child in node.children:
        yield from walk_asn1(child)


def find_spc_indirect_data_node(pkcs7_blob: bytes) -> Asn1Node | None:
    root, _ = read_asn1_node(pkcs7_blob)
    nodes = list(walk_asn1(root))
    for idx, node in enumerate(nodes):
        if node.tag == 0x06 and decode_oid(node.value) == OID_SPC_INDIRECT_DATA:
            for candidate in nodes[idx + 1 : idx + 8]:
                if candidate.tag == 0x04:
                    content, _ = read_asn1_node(candidate.value)
                    return content
                if candidate.tag == 0xA0 and candidate.children:
                    return candidate.children[0]
                if candidate.tag == 0x30 and candidate.children:
                    return candidate
    return None


def extract_expected_authenticode_digest(pkcs7_blob: bytes) -> dict[str, Any] | None:
    root = find_spc_indirect_data_node(pkcs7_blob)
    if root is None:
        return None

    sequences = [node for node in walk_asn1(root) if node.tag == 0x30]
    for seq in reversed(sequences):
        if len(seq.children) < 2:
            continue
        alg_seq = seq.children[0]
        digest_node = seq.children[1]
        if alg_seq.tag != 0x30 or digest_node.tag != 0x04:
            continue
        oid_nodes = [child for child in alg_seq.children if child.tag == 0x06]
        if not oid_nodes:
            continue
        oid = decode_oid(oid_nodes[0].value)
        alg = OID_DIGEST_ALGS.get(oid)
        if alg:
            return {"algorithm": alg, "oid": oid, "digest": digest_node.value.hex()}
    return None


def trim_asn1_tlv(data: bytes) -> bytes:
    if len(data) < 2 or data[0] != 0x30:
        return data

    first_len = data[1]
    if first_len < 0x80:
        total = 2 + first_len
    else:
        len_len = first_len & 0x7F
        if len_len == 0 or len_len > 4 or len(data) < 2 + len_len:
            return data
        total = 2 + len_len + int.from_bytes(data[2 : 2 + len_len], "big")

    if 0 < total <= len(data):
        return data[:total]
    return data


def load_win_certificate(path: Path) -> WinCertificate:
    pe = pefile.PE(str(path), fast_load=True)
    try:
        sec_idx = pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]
        security_dir = pe.OPTIONAL_HEADER.DATA_DIRECTORY[sec_idx]
        offset = int(security_dir.VirtualAddress)
        size = int(security_dir.Size)
        if offset == 0 or size < 8:
            raise ValueError("Unsigned PE: no IMAGE_DIRECTORY_ENTRY_SECURITY")

        data = path.read_bytes()
        if offset + size > len(data):
            raise ValueError("Invalid SECURITY table: exceeds end of file")

        length = int.from_bytes(data[offset : offset + 4], "little")
        revision = int.from_bytes(data[offset + 4 : offset + 6], "little")
        cert_type = int.from_bytes(data[offset + 6 : offset + 8], "little")
        if length < 8 or length > size:
            raise ValueError(f"Invalid WIN_CERTIFICATE: length={length}, size={size}")

        blob = trim_asn1_tlv(data[offset + 8 : offset + length])
        return WinCertificate(length, revision, cert_type, blob)
    finally:
        pe.close()


def authenticode_hash(path: Path, algorithm: str) -> dict[str, Any]:
    data = path.read_bytes()
    pe = pefile.PE(str(path), fast_load=True)
    try:
        sec_idx = pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]
        security_dir = pe.OPTIONAL_HEADER.DATA_DIRECTORY[sec_idx]
        cert_offset = int(security_dir.VirtualAddress)
        cert_size = int(security_dir.Size)
        if not cert_offset or not cert_size:
            raise ValueError("Unsigned PE: no SECURITY directory")

        pe_offset = int(pe.DOS_HEADER.e_lfanew)
        optional_offset = pe_offset + 4 + pefile.Structure(pe.__IMAGE_FILE_HEADER_format__).sizeof()
        checksum_offset = optional_offset + 64
        data_dir_offset = optional_offset + int(pe.FILE_HEADER.SizeOfOptionalHeader) - (
            int(pe.OPTIONAL_HEADER.NumberOfRvaAndSizes) * 8
        )
        security_dir_entry_offset = data_dir_offset + (sec_idx * 8)

        excluded = [
            (checksum_offset, checksum_offset + 4, "checksum"),
            (
                security_dir_entry_offset,
                security_dir_entry_offset + 8,
                "security_directory_entry",
            ),
            (cert_offset, cert_offset + cert_size, "certificate_table"),
        ]
        for start, end, name in excluded:
            if start < 0 or end > len(data) or start > end:
                raise ValueError(f"Invalid Authenticode offset: {name}")

        digest = hashlib.new(algorithm)
        pos = 0
        hashed_ranges: list[dict[str, Any]] = []
        for start, end, name in sorted(excluded):
            if pos < start:
                digest.update(data[pos:start])
                hashed_ranges.append({"start": pos, "end": start, "size": start - pos})
            pos = max(pos, end)
        if pos < len(data):
            digest.update(data[pos:])
            hashed_ranges.append({"start": pos, "end": len(data), "size": len(data) - pos})

        return {
            "algorithm": algorithm,
            "digest": digest.hexdigest(),
            "excluded": [
                {"name": name, "start": start, "end": end, "size": end - start}
                for start, end, name in excluded
            ],
            "hashed_ranges": hashed_ranges,
            "file_size": len(data),
        }
    finally:
        pe.close()


def cert_sha256(cert: x509.Certificate) -> str:
    return cert.fingerprint(hashes.SHA256()).hex()


def rfc4514(name: x509.Name) -> str:
    return name.rfc4514_string()


def cert_to_dict(cert: x509.Certificate) -> dict[str, Any]:
    now = datetime.now(UTC)
    not_before = cert.not_valid_before_utc
    not_after = cert.not_valid_after_utc
    eku: list[str] | None
    has_code_signing = False

    try:
        eku_ext = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
        eku = [oid.dotted_string for oid in eku_ext.value]
        has_code_signing = ExtendedKeyUsageOID.CODE_SIGNING in eku_ext.value
    except x509.ExtensionNotFound:
        eku = None

    ca_issuers: list[str] = []
    try:
        aia_ext = cert.extensions.get_extension_for_class(x509.AuthorityInformationAccess)
        for access in aia_ext.value:
            if access.access_method == AuthorityInformationAccessOID.CA_ISSUERS:
                ca_issuers.append(access.access_location.value)
    except x509.ExtensionNotFound:
        pass

    return {
        "subject": rfc4514(cert.subject),
        "issuer": rfc4514(cert.issuer),
        "serial": hex(cert.serial_number),
        "sha256": cert_sha256(cert),
        "not_before": not_before.isoformat(),
        "not_after": not_after.isoformat(),
        "currently_valid": not_before <= now <= not_after,
        "eku": eku,
        "has_code_signing_eku": has_code_signing,
        "ca_issuers": ca_issuers,
        "self_signed_name": cert.subject == cert.issuer,
    }


def choose_leaf(certs: list[x509.Certificate]) -> x509.Certificate:
    issuers = {rfc4514(cert.issuer) for cert in certs if cert.subject != cert.issuer}
    leaves = [cert for cert in certs if rfc4514(cert.subject) not in issuers]

    code_signing_leaves = []
    for cert in leaves:
        try:
            eku_ext = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
        except x509.ExtensionNotFound:
            continue
        if ExtendedKeyUsageOID.CODE_SIGNING in eku_ext.value:
            code_signing_leaves.append(cert)

    if code_signing_leaves:
        return code_signing_leaves[0]
    if leaves:
        return leaves[0]
    return certs[0]


def write_pem(path: Path, certs: list[x509.Certificate]) -> None:
    path.write_bytes(
        b"".join(cert.public_bytes(serialization.Encoding.PEM) for cert in certs)
    )


def load_cert_bytes(data: bytes) -> x509.Certificate:
    if data.lstrip().startswith(b"-----BEGIN CERTIFICATE-----"):
        return x509.load_pem_x509_certificate(data)
    return x509.load_der_x509_certificate(data)


def safe_cert_filename(cert: x509.Certificate) -> str:
    attrs = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    cn = attrs[0].value if attrs else cert_sha256(cert)[:12]
    safe = "".join(ch if ch.isalnum() else "_" for ch in cn).strip("_")
    return f"{safe}_{cert_sha256(cert)[:12]}.pem"


def rebuild_ca_bundle(cert_dir: Path) -> Path:
    bundle = cert_dir / "ca-bundle.pem"
    pem_files = sorted(
        path for path in cert_dir.glob("*.pem") if path.name != "ca-bundle.pem"
    )
    bundle.write_bytes(b"".join(path.read_bytes() for path in pem_files))
    return bundle


def fetch_aia_certs(certs: list[x509.Certificate], cert_dir: Path) -> dict[str, Any]:
    cert_dir.mkdir(parents=True, exist_ok=True)
    fetched: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    urls = sorted({url for cert in certs for url in cert_to_dict(cert)["ca_issuers"]})

    for url in urls:
        try:
            with urlopen(url, timeout=15) as response:
                data = response.read()
            cert = load_cert_bytes(data)
            out_path = cert_dir / safe_cert_filename(cert)
            out_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            fetched.append(
                {
                    "url": url,
                    "path": str(out_path),
                    "subject": rfc4514(cert.subject),
                    "sha256": cert_sha256(cert),
                }
            )
        except Exception as exc:
            errors.append({"url": url, "error": str(exc)})

    bundle = rebuild_ca_bundle(cert_dir)
    return {"fetched": fetched, "errors": errors, "bundle": str(bundle)}


def run_openssl(args: list[str], input_data: bytes | None = None) -> dict[str, Any]:
    exe = shutil.which("openssl")
    if not exe:
        return {"ok": None, "error": "openssl not found"}
    proc = subprocess.run(
        [exe, *args],
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", errors="replace").strip(),
        "stderr": proc.stderr.decode("utf-8", errors="replace").strip(),
    }


def openssl_pkcs7_verify(blob: bytes) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pe-cert-") as tmp:
        sig_path = Path(tmp) / "sig.p7b"
        sig_path.write_bytes(blob)
        return run_openssl(
            ["cms", "-verify", "-inform", "DER", "-in", str(sig_path), "-noverify", "-out", "/dev/null"]
        )


def openssl_chain_verify(
    leaf: x509.Certificate,
    certs: list[x509.Certificate],
    ca_file: str | None,
    ca_path: str | None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="pe-cert-") as tmp:
        tmp_path = Path(tmp)
        leaf_path = tmp_path / "leaf.pem"
        chain_path = tmp_path / "chain.pem"
        others = [cert for cert in certs if cert_sha256(cert) != cert_sha256(leaf)]
        write_pem(leaf_path, [leaf])
        write_pem(chain_path, others)

        args = ["verify", "-purpose", "any"]
        if ca_file:
            args.extend(["-CAfile", ca_file])
        if ca_path:
            args.extend(["-CApath", ca_path])
        if others:
            args.extend(["-untrusted", str(chain_path)])
        args.append(str(leaf_path))
        return run_openssl(args)


def analyze(
    path: Path,
    ca_file: str | None,
    ca_path: str | None,
    use_openssl: bool,
    check_pkcs7: bool,
    fetch_aia: bool,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    win_cert = load_win_certificate(path)
    expected_digest = extract_expected_authenticode_digest(win_cert.blob)
    result: dict[str, Any] = {
        "file": str(path),
        "signed": True,
        "win_certificate": {
            "length": win_cert.length,
            "revision": hex(win_cert.revision),
            "revision_ok": win_cert.revision == WIN_CERT_REVISION_2_0,
            "type": hex(win_cert.cert_type),
            "type_ok": win_cert.cert_type == WIN_CERT_TYPE_PKCS_SIGNED_DATA,
        },
    }
    if expected_digest:
        computed_digest = authenticode_hash(path, expected_digest["algorithm"])
        result["authenticode_hash"] = {
            "embedded": expected_digest,
            "computed": computed_digest,
            "match": computed_digest["digest"].lower()
            == expected_digest["digest"].lower(),
        }
    else:
        result["authenticode_hash"] = {
            "embedded": None,
            "computed": authenticode_hash(path, "sha256"),
            "match": None,
        }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        certs = pkcs7.load_der_pkcs7_certificates(win_cert.blob)
    result["certificate_count"] = len(certs)
    if not certs:
        result["ok"] = False
        result["errors"] = ["PKCS#7 has no certificate"]
        return result

    leaf = choose_leaf(certs)
    leaf_info = cert_to_dict(leaf)
    result["leaf"] = leaf_info
    result["certificates"] = [cert_to_dict(cert) for cert in certs]

    default_cert_dir = Path(__file__).resolve().parent / "certificates"
    if fetch_aia:
        result["fetch_aia"] = fetch_aia_certs(certs, default_cert_dir)
        if not ca_file:
            ca_file = result["fetch_aia"]["bundle"]

    errors: list[str] = []
    warn_msgs: list[str] = []
    if not result["win_certificate"]["revision_ok"]:
        warn_msgs.append("Unexpected WIN_CERTIFICATE revision")
    if not result["win_certificate"]["type_ok"]:
        errors.append("WIN_CERTIFICATE type is not PKCS_SIGNED_DATA")
    if not leaf_info["currently_valid"]:
        errors.append("Leaf certificate expired or not yet valid")
    if leaf_info["eku"] is not None and not leaf_info["has_code_signing_eku"]:
        errors.append("Leaf certificate lacks Code Signing EKU")
    if leaf_info["eku"] is None:
        warn_msgs.append("Leaf certificate has no EKU extension")
    auth_hash = result["authenticode_hash"]
    if auth_hash["match"] is False:
        errors.append("Recomputed Authenticode hash differs from signed hash")
    if auth_hash["match"] is None:
        warn_msgs.append("Signed Authenticode digest not extracted; only recomputed sha256 shown")

    if use_openssl:
        if not ca_file:
            default_ca = default_cert_dir / "ca-bundle.pem"
            if default_ca.exists():
                ca_file = str(default_ca)

        if check_pkcs7:
            result["pkcs7_verify"] = openssl_pkcs7_verify(win_cert.blob)
            if result["pkcs7_verify"]["ok"] is False:
                warn_msgs.append("OpenSSL cms -verify failed")

        result["chain_verify"] = openssl_chain_verify(leaf, certs, ca_file, ca_path)
        if result["chain_verify"]["ok"] is False:
            errors.append("Certificate chain not validated by OpenSSL")
            result["chain_hint_ca_issuers"] = sorted(
                {
                    url
                    for cert in certs
                    for url in cert_to_dict(cert).get("ca_issuers", [])
                }
            )
    else:
        warn_msgs.append("OpenSSL checks disabled")

    result["errors"] = errors
    result["warnings"] = warn_msgs
    result["ok"] = not errors
    return result


def print_text(result: dict[str, Any]) -> None:
    print(f"File: {result['file']}")
    print(f"Signed: {result['signed']}")
    if "win_certificate" not in result:
        if result.get("errors"):
            print("Errors:")
            for error in result["errors"]:
                print(f"  - {error}")
        print(f"OK: {result['ok']}")
        return

    wc = result["win_certificate"]
    print(
        "WIN_CERTIFICATE: "
        f"length={wc['length']} revision={wc['revision']} type={wc['type']}"
    )
    print(f"Certificates: {result.get('certificate_count', 0)}")
    auth_hash = result.get("authenticode_hash")
    if auth_hash:
        print("Authenticode hash:")
        embedded = auth_hash.get("embedded")
        computed = auth_hash.get("computed")
        if embedded:
            print(f"  Algorithm: {embedded['algorithm']} ({embedded['oid']})")
            print(f"  Embedded:  {embedded['digest']}")
        if computed:
            print(f"  Computed:  {computed['digest']}")
        print(f"  Match:     {auth_hash['match']}")

    leaf = result.get("leaf")
    if leaf:
        print("Leaf:")
        print(f"  Subject: {leaf['subject']}")
        print(f"  Issuer:  {leaf['issuer']}")
        print(f"  Serial:  {leaf['serial']}")
        print(f"  SHA256:  {leaf['sha256']}")
        print(f"  Valid:   {leaf['not_before']} -> {leaf['not_after']}")
        print(f"  Now OK:  {leaf['currently_valid']}")
        print(f"  CodeSign EKU: {leaf['has_code_signing_eku']}")
        if leaf.get("ca_issuers"):
            print("  CA Issuers:")
            for url in leaf["ca_issuers"]:
                print(f"    {url}")

    for key in ("pkcs7_verify", "chain_verify"):
        if key in result:
            item = result[key]
            print(f"{key}: {item.get('ok')}")
            msg = item.get("stderr") or item.get("stdout") or item.get("error")
            if msg:
                print(f"  {msg}")

    if result.get("fetch_aia"):
        fetched = result["fetch_aia"]["fetched"]
        failed = result["fetch_aia"]["errors"]
        print(f"fetch_aia: fetched={len(fetched)} failed={len(failed)}")
        for item in fetched:
            print(f"  + {item['path']}")
        for item in failed:
            print(f"  - {item['url']}: {item['error']}")

    if result.get("warnings"):
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
    if result.get("errors"):
        print("Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
    if result.get("chain_hint_ca_issuers"):
        print("CA Issuers hints:")
        for url in result["chain_hint_ca_issuers"]:
            print(f"  - {url}")
    print(f"OK: {result['ok']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PE embedded certificates")
    parser.add_argument("pe", type=Path, help="PE file: .exe/.dll/.sys")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--ca-file", help="CA bundle for openssl verify")
    parser.add_argument("--ca-path", help="CA directory for openssl verify")
    parser.add_argument("--no-openssl", action="store_true", help="Skip OpenSSL checks")
    parser.add_argument(
        "--check-pkcs7",
        action="store_true",
        help="Try OpenSSL cms -verify on PKCS#7 blob; may fail on Authenticode SPC",
    )
    parser.add_argument(
        "--fetch-aia",
        action="store_true",
        help="Download CA Issuers AIA certificates into ./certificates and rebuild ca-bundle.pem",
    )
    args = parser.parse_args()

    try:
        result = analyze(
            args.pe,
            args.ca_file,
            args.ca_path,
            not args.no_openssl,
            args.check_pkcs7,
            args.fetch_aia,
        )
    except Exception as exc:
        result = {"file": str(args.pe), "signed": False, "ok": False, "errors": [str(exc)]}

    if args.json:
        print((json.dumps(result, indent=2, sort_keys=True)))
    else:
        print_text(result)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
