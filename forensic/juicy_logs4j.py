#!/usr/bin/env python3
# coding=utf-8
import sys
import re
import string
import socket
from struct import unpack
from socket import AF_INET, inet_pton


DNS_CACHE = {}


# Functions
def getparam(count):
    """Retrieve the parameters appended """
    if len(sys.argv) != count + 1:
        print('extract log4j abuse attempt')
        print('To Use: %s anytextlogfile' % sys.argv[0])
        sys.exit(1)
    else:
        return sys.argv[1]


def dnsresolv(host):
    ''' Resolve a dns, implement a caching '''
    ''' return an array of ip's '''
    resolvedIP = DNS_CACHE.get('host')

    if not resolvedIP:
        try:
            resolvedIP = socket.gethostbyaddr(host)
        except socket.herror:
            resolvedIP = socket.gethostbyname(host)
            resolvedIP = ('', '', [resolvedIP])
        except socket.gaierror:
            return(None)

    if resolvedIP:
        DNS_CACHE[host] = resolvedIP
        outip = []
        for ip in resolvedIP[2]:
            outip.append(ip)
        return(outip)


def resolv(line):
    ''' Extract a hostname, don't care it it's an ip in input '''
    regex = re.compile(r"(ldap|dns|rmi):\/\/?(?P<host>[a-z\-.0-9]+)(\/|:)")
    host = re.search(regex, line)
    if host:
        # Check if it's an IP
        ip = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        isip = re.search(ip, host.group("host"))
        if isip:
            return(None)
        # return an arry of IP's
        return(dnsresolv(host.group("host")))


def splits(line):
    ''' Split a line on comma, respect quotes '''
    regex = re.compile(r"\\.|[\"',]", re.DOTALL)
    delimiter = ''
    compos = [-1]
    for match in regex.finditer(line):
        g = match.group(0)
        if delimiter == '':
            if g == ',':
                compos.append(match.start())
            elif g in "\"'":
                delimiter = g
        elif g == delimiter:
            delimiter = ''
    compos.append(len(line))
    return [line[compos[i] + 1:compos[i + 1]] for i in range(len(compos)- 1)]


def private(ip):
    ''' return only public ip's '''
    # pepom de
    # https://www.techtalk7.com/how-do-you-determine-if-an-ip-address-is-private-in-python/
    if ip == "0.0.0.0":
        return(True)
    try:
        f = unpack('!I', inet_pton(AF_INET, ip))[0]
    except OSError:
        return(True)
    private = (
        [2130706432, 4278190080],  # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
        [3232235520, 4294901760],  # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
        [2886729728, 4293918720],  # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
        [167772160, 4278190080],  # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
    )
    for net in private:
        if (f & net[1]) == net[0]:
            return True
    return False


def uniq_ext(ips):
    ''' | sort | uniq an arry of ips '''
    ''' let out only external one '''
    outip = []
    ips = list(set(ips))
    for ip in ips:
        if not private(ip):
            outip.append(ip)
    return(outip)


def scan(line, num):
    ''' main "stuff '''

    # if b64
    b64 = ""
    # attrape les base64/
    if "ase64/" in line:
        b64c = re.search(r'(?P<nop>ase64\/)(?P<b64>[a-zA-Z0-9+\/]{32,}={0,2})', line)
        if b64c:
            b64 = b64c.group('b64')

    # Remplace les anchors strtolower qu'on soit sur du ${ et des :
    line = re.sub('%24', '$', line.lower())
    for char in [('7b', '{'), ('7d', '}'), ('3a', ':'), ('2f', '/')]:
        line = line.replace(f"%{char[0]}", char[1])

    line = line.replace("${hostname}", "VAR_HOSTNAME")
    #  ${lower:l}   to l
    if "::-" in line:
        for letter in string.ascii_lowercase:
            cand = "${::-" + letter + "}"
            line = line.replace(cand, letter)
    if "env:env_name" in line:
        # ${env:ENV_NAME:-
        for letter in string.ascii_lowercase:
            cand = "${env:env_name:-" + letter + "}"
            line = line.replace(cand, letter)
        line = line.replace("${env:env_name:-:", ":")
    if "lower" in line:
        for letter in string.ascii_lowercase:
            cand = "${lower:" + letter + "}"
            line = line.replace(cand, letter)
    if "upper" in line:
        for letter in string.ascii_lowercase:
            cand = "${upper:" + letter + "}"
            line = line.replace(cand, letter)

    # Split le CSV, pour simplifier la vie de la regex.
    csv_line = splits(line)
    # declaring the regex pattern for IP addresses
    ip = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    # initializing the list object
    outip=[]
    # extracting the IP addresses sur la ligne de log
    outip = ip.findall(line)

    # Cherche la patterne ${.*}
    pattern = r"\$\{(.+?)(\}| |,|$|\\r)"
    for row in csv_line:
        if "${" in row:
            items = re.findall(pattern, row)
            for item in items:
                for toto in item:
                    toto = toto.replace("jndi:", "")
                    for word in ["dns", "ldap", "rmi"]:
                        if word in toto:
                            addip = resolv(toto)
                            if addip:
                                outip = outip + addip
                            outip = uniq_ext(outip)
                            print(f"line:{num}|{toto}|{outip}|{b64}")


# Main Code #####
def main():
    param = getparam(1)
    f = open(param, "rt")
    num = 0
    for line in f.readlines():
        num += 1
        scan(line, num)


if __name__ == '__main__':
    main()
