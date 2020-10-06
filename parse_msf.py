#!/usr/bin/env python3
# coding=utf-8
import sys
import re


# Functions
def getparam(count):
    """Retrieve the parameters appended """
    if len(sys.argv) != count + 1:
        print('Parse MSF History')
        print('To Use: %s mymsffile' % sys.argv[0])
        sys.exit(1)
    else:
        return sys.argv[1]


def noempty(text):
    text = text.split('\n')
    out = []
    for line in text:
        line.strip()
        line = line.replace("\r", "")
        # Remove duplicate spaces in line.
        line = re.sub(r'  *', ' ', line)
        if line not in ['', ' ']:
            # Shoot " truc" and "truc "
            if line[0] == ' ':
                line = line[1::]
            if line[len(line) - 1] == ' ':
                line = line[:-1]
            out.append(line)
    return("\n".join(out))


# Main Code #####
def main():
    msffile = getparam(1)
    f = open(msffile, "r")
    msfbuffer = noempty(f.read()).split('\n')

    actions, ctuples, chosts = [], [], []
    rhost, search, smbuser, smbpass, smbdomain = "", "", "", "", '.'
    for line in msfbuffer:
        # print("->" + line)
        out = re.match(r'^set RHOST (?P<rhost>.*)', line)
        if out:
            rhost = out.group('rhost')
            continue
        out = re.match(r'^search (?P<search>.*)', line)
        if out:
            search = out.group('search')
            continue
        out = re.match(r'^set SMBUser (?P<smbuser>.*)', line)
        if out:
            smbuser = out.group('smbuser')
            continue
        out = re.match(r'^set SMBPass (?P<smbpass>.*)', line)
        if out:
            smbpass = out.group('smbpass')
            continue
        out = re.match(r'^set SMBDomain (?P<smbdomain>.*)', line)
        if out:
            smbdomain = out.group('smbdomain')
            continue
        out = re.match(r'^use (?P<action>.*)', line)
        if out:
            if re.match(r'^\d+$', out.group('action')):
                action = f"Search {search}|{out.group('action')}"
            else:
                action = out.group('action')
        if line == "exploit" or line=='run':
            actions.append(f"{action} on {rhost} with {smbdomain}\\{smbuser} {smbpass}")
            ctuples.append(f"{smbdomain}\\{smbuser} {smbpass}")
            chosts.append(f"{rhost}")

    # pipe sort uniq
    actions = list(set(actions))
    ctuples = list(set(ctuples))
    chosts = list(set(chosts))

    print("Logged actions")
    for action in actions:
        print (action)
    print("\nCompromised Credentials")
    for ctuple in ctuples:
        print (ctuple)
    print("\nCompromised Hosts")
    for chost in chosts:
        print (chost)






if __name__ == '__main__':
    main()
