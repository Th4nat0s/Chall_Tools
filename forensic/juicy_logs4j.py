#!/usr/bin/env python3
# coding=utf-8
import sys
import re
import string
from csv import DictReader, reader
from struct import unpack
from socket import AF_INET, inet_pton


# Functions
def getparam(count):
    """Retrieve the parameters appended """
    if len(sys.argv) != count + 1:
        print('My command')
        print('To Use: %s my params' % sys.argv[0])
        sys.exit(1)
    else:
        return sys.argv[1]


def splits(line):
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


def scan(line, num):

    # if b64
    b64 = ""
    # attrape les base64/
    if "ase64/" in line:
        b64 = re.findall(r'(?P<b64>ase64\/[a-zA-Z0-9+\/]{32,}={0,2})', line)

    # Remplace les anchors strtolower qu'on soit sur du ${
    line = re.sub('%24', '$', line.lower())
    for char in [('%7b', '{'), ('%7d', '}')]:
        line = line.replace(char[0], char[1])

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
    lst=[]
    # extracting the IP addresses sur la ligne de log
    lst = ip.findall(line)
    lst = list(set(lst))
    outip = []
    for ip in lst:
        if not private(ip):
            outip.append(ip)

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
