#!/usr/bin/env python3
# coding=utf-8
# Author: Joe Slowik
# Free for use under GPL3+
# Purpose: Port of Michael Ligh's pescanner.py to Python3 - for reasons.

import os
import sys
import time
import hashlib
import pefile
import magic
import re
import string
import exifread


def header(msg):
    return "\n" + msg + "\n" + ("=" * 90)


def subTitle(msg):
    return msg + "\n" + ("-" * 40)


def convert_char(char):
    if char in string.ascii_letters or \
       char in string.digits or \
       char in string.punctuation or \
       char in string.whitespace:
        return char
    else:
        return r'\x%02x' % ord(char)


def convert_to_printable(s):
    return ''.join([convert_char(c) for c in s])


# suspicious APIs to alert on
alerts = ['OpenProcess', 'VirtualAllocEx', 'WriteProcessMemory', 'CreateRemoteThread', 'ReadProcessMemory',
          'CreateProcess', 'WinExec', 'ShellExecute', 'HttpSendRequest', 'InternetReadFile', 'InternetConnect',
          'CreateService', 'StartService']

# legit entry point sections
good_ep_sections = ['.text', '.code', 'CODE', 'INIT', 'PAGE']

stringSearch = ['GET', 'POST', 'ssh', 'ftp', 'http', 'irc', '.exe', '.dll', '.scr', '.ini', '.bat', 'wmi', 'powershell',
                'cmd', 'regedit', 'HKEY', 'HKCU', 'CurrentVersion', 'appdata', 'temp', 'system32', 'syswow64', 'pipe',
                'wscript', 'startup', 'run', 'del', '.com', 'org', '.edu', '.ru', '.cn', '.net', 'www', '.ir', '.xyz',
                '.il', '.download', '.tor', '.onion', 'vbscript']


def get_filetype(data):
    if 'magic' in sys.modules:
        try:
            ms = magic.open(magic.MAGIC_NONE)
            ms.load()
            magictype = ms.buffer(data)
            ms.close()
            return magictype
        except:
            try:
                return magic.from_buffer(data)
            except magic.MagicException:
                magic_custom = magic.Magic(magic_file='C:\windows\system32\magic')
                return magic_custom.from_buffer(data)
    return ''


class peTesting:
    def __init__(self, files, yara_rules=None, peid_sigs=None):
        self.files = files

        # initialize YARA rules if provided
        if yara_rules and 'yara' in sys.modules:
            self.rules = yara.compile(yara_rules)
        else:
            self.rules = None

        # initialize PEiD signatures if provided
        if peid_sigs:
            self.sigs = peutils.SignatureDatabase(peid_sigs)
        else:
            self.sigs = None

    def check_ep_section(self, pe):
        """ Determine if a PE's entry point is suspicious """
        name = ''
        ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
        pos = 0
        for sec in pe.sections:
            if (ep >= sec.VirtualAddress) and \
                    (ep < (sec.VirtualAddress + sec.Misc_VirtualSize)):
                name = sec.Name.decode(encoding='UTF-8')
                break
            else:
                pos += 1
        return (ep, name, pos)

    def get_timestamp(self, pe):
        val = pe.FILE_HEADER.TimeDateStamp
        ts = '0x%-8X' % (val)
        try:
            ts += ' [%s UTC]' % time.asctime(time.gmtime(val))
            that_year = time.gmtime(val)[0]
            this_year = time.gmtime(time.time())[0]
            if that_year < 2000 or that_year > this_year:
                ts += " [SUSPICIOUS]"
        except:
            ts += ' [SUSPICIOUS]'
        return ts

    def get_lang(self, pe):
        resources = self.check_rsrc(pe)
        ret = []
        lang_holder = []
        for rsrc in resources.keys():
            (name, rva, size, type, lang, sublang) = resources[rsrc]
            ret = lang +', ' + sublang
        return ret

    def check_strings(self):
        print(files)
        recognizedChars = r"A-Za-z0-9/\-:.,_$%'()[\]<> "
        stringLength = 4
        strRegexp = '[%s]{%d,}' % (recognizedChars, stringLength)
        searchPattern = re.compile(strRegexp)
        with open(str(files).strip("[]'"), "r") as file:
            print(get_filetype(file))
            result = ""
            stringList = re.split(str(file), not string.printable)
            # stringList = searchPattern.search(file)
            print(stringList)
        return result

    def check_packers(self, pe):
        packers = []
        if self.sigs:
            matches = self.sigs.match(pe, ep_only=True)
            if matches != None:
                for match in matches:
                    packers.append(match)
        return packers

    def check_rsrc(self, pe):
        ret = {}
        if hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE'):
            i = 0
            for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                if resource_type.name is not None:
                    name = "%s" % resource_type.name
                else:
                    name = "%s" % pefile.RESOURCE_TYPE.get(resource_type.struct.Id)
                if name is None:
                    name = "%d" % resource_type.struct.Id
                if hasattr(resource_type, 'directory'):
                    for resource_id in resource_type.directory.entries:
                        if hasattr(resource_id, 'directory'):
                            for resource_lang in resource_id.directory.entries:
                                data = pe.get_data(resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size)
                                if 'magic' in sys.modules:
                                    if sys.version_info <= (2, 6):
                                        filetype = self.ms.buffer(data)
                                    else:
                                        # filetype = magic._buffer(data)
                                        filetype = "Magic Error"
                                    lang = pefile.LANG.get(resource_lang.data.lang, '*unknown*')
                                    sublang = pefile.get_sublang_name_for_lang(resource_lang.data.lang, resource_lang.data.sublang)
                                else:
                                    filetype = None
                                if filetype == None:
                                    filetype = ''
                                ret[i] = (name, resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size, filetype, lang, sublang)
                                i += 1
        return ret

    def check_imports(self, pe):
        ret = []
        if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            return ret
        for lib in pe.DIRECTORY_ENTRY_IMPORT:
            for imp in lib.imports:
                if(imp.name is not None) and (imp.name != ''):
                    for alert in alerts:
                        if imp.name.startswith(alert.encode()):
                            ret.append(imp.name)
        return ret

    def check_yara(self, data):
        ret = []
        if self.rules:
            yarahits = self.rules.match(data=data)
            if yarahits:
                for hit in yarahits:
                    ret.append("YARA: %s" % hit.rule)
                    # for key, val in hit.strings.iteritems():
                    for (key, stringname, val) in hit.strings:
                        makehex = False
                        for char in val:
                            if char not in string.printable:
                                makehex = True
                                break
                        if makehex is True:
                            ret.append("\t%s => %s" % (hex(key), binascii.hexlify(val)))
                        else:
                            ret.append("\t %s => %s" % (hex(key), val))
        return '\n'.join(ret)

    def get_exif(self):
        exifData = open(str(files).strip("[]'"))
        exifOut = ''
        for item in exifData:
            exifOut.append(str(item))
        return exifOut

    def collect(self, verb):
        count = 0

        for file in self.files:
            out = []

            try:
                FILE = open(file, "rb")
                data = FILE.read()
                FILE.close()
            except:
                continue

            if data == None or len(data) == 0:
                out.append("Cannot read %s (maybe empty?)" % file)
                out.append("")
                continue

            try:
                pe = pefile.PE(data=data, fast_load=True)
                pe.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                    pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
                    pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
                    pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
            except:
                out.append("Cannot parse %s (maybe not PE?)" % file)
                out.append("")
                continue

            # source: https://code.google.com/p/pyew/
            def get_filearch(data):
                if pe.FILE_HEADER.Machine == 0x14C:  # IMAGE_FILE_MACHINE_I386
                    processor = "intel"
                    type = 32
                    return "32 Bits binary"
                elif pe.FILE_HEADER.Machine == 0x8664:  # IMAGE_FILE_MACHINE_AMD64
                    processor = "intel"
                    type = 64
                    return "64 Bits binary"

            out.append(("#" * 90) + "\n[%d] File: %s\n" % (count, file) + ("#" * 90))
            out.append(header("Meta-data"))
            out.append("Size\t\t: %d bytes" % len(data))
            out.append("Type\t\t: %s" % get_filetype(data))
            out.append("Architecture\t: %s" % get_filearch(data))
            out.append("MD5\t\t: %s" % hashlib.md5(data).hexdigest())
            out.append("SHA1\t\t: %s" % hashlib.sha1(data).hexdigest())
            out.append("SHA256\t\t: %s" % hashlib.sha256(data).hexdigest())
            out.append("Date\t\t: %s" % self.get_timestamp(pe))
            crc_claimed = pe.OPTIONAL_HEADER.CheckSum
            crc_actual = pe.generate_checksum()
            out.append("CRC:\t(Claimed) : 0x%x, (Actual): 0x%x %s" % (
                crc_claimed, crc_actual, "[SUSPICIOUS]" if crc_actual != crc_claimed else ""))
            out.append("Language\t: %s" % self.get_lang(pe))

            packers = self.check_packers(pe)
            if len(packers):
                out.append("Packers\t\t: %s" % ','.join(packers))

            # Alert if the EP section is not in a known good section or if its in the last PE section
            (ep, name, pos) = self.check_ep_section(pe)
            ep_ava = ep + pe.OPTIONAL_HEADER.ImageBase
            s = "Entry Point\t: %s %s %d/%d" % (hex(ep_ava), name, pos, len(pe.sections))
            if (name not in good_ep_sections) or pos == len(pe.sections):
                s += " [SUSPICIOUS]"
            out.append(s)

            if 'yara' in sys.modules:
                yarahits = self.check_yara(data)
            else:
                yarahits = []

            if len(yarahits):
                out.append(header("Signature scans"))
                out.append(yarahits)
                out.append(clamhits)

            out.append(header("Sections"))
            out.append(
                "%-10s %-12s %-12s %-10s %-12s %27s" % ("Name", "VirtAddr", "VirtSize", "RawSize", "MD5", "Entropy"))
            out.append("-" * 90)

            for sec in pe.sections:
                s = "%-12s %-12s %-12s %-10s %-12s %-12f" % (
                    # ''.join([str(ord(x)) for x in sec.Name]), #if str(c).isprintable()]),
                    sec.Name.decode(encoding='UTF-8'),
                    hex(sec.VirtualAddress),
                    hex(sec.Misc_VirtualSize),
                    hex(sec.SizeOfRawData),
                    sec.get_hash_md5(),
                    sec.get_entropy())
                if sec.SizeOfRawData == 0 or (sec.get_entropy() > 0 and sec.get_entropy() < 1) or sec.get_entropy() > 7:
                    s += "[SUSPICIOUS]"
                out.append(s)

            imports = self.check_imports(pe)
            if len(imports):
                out.append(header("Suspicious Imports"))
                for imp in imports:
                    out.append(str(imp))

            imports_total = len(pe.DIRECTORY_ENTRY_IMPORT)
            if imports_total > 0:
                c = 1
                out.append(header("Imports"))
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    out.append("[%s] %s" % (c,entry.dll))
                    if verb is True:
                        for imp in entry.imports:
                            if (imp.name != None) and (imp.name != ""):
                                out.append("\t%s %s" % (hex(imp.address),imp.name))
                    c += 1

            # Grab the exports info , if available
            if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
                c = 1
                out.append(header("Exports"))
                for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    if verb is True:
                        out.append("[%s] %s %s" % (c, hex(exp.address), exp.name))
                    else:
                        out.append("[%s] %s" % (c, exp.name))
                    c += 1

            out.append("")
            print('\n'.join(out))
            count += 1

            # out.append("EXIF Data:\n %s" % self.get_exif())

            # out.append("Strings:\n %s" % self.check_strings())


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: %s <file|directory>\n" % (sys.argv[0]))
        sys.exit()

    object = sys.argv[1]
    files = []

    if os.path.isdir(object):
        for root, dirs, filenames in os.walk(object):
            for name in filenames:
                files.append(os.path.join(root, name))
    elif os.path.isfile(object):
        files.append(object)
    else:
        print("You must supply a file or directory!")
        sys.exit()

    verb = False
    # You should fill these in with a path to your YARA rules and PEiD database
    pescan = peTesting(files, '', '')
    pescan.collect(verb)
