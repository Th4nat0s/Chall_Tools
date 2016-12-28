#!/usr/bin/env python
# coding=utf-8
import re
import sys
import string


# Functions
def getparam(count):
    if len(sys.argv) != count + 1:
        print 'Convert a static string to static regex case insensitive for bulk_extractor option -F'
        print 'To Use: ' + sys.argv[0] + ' infile outfile'
        sys.exit(1)
    else:
        return sys.argv[1], sys.argv[2]


# Main Code #####
def main():
    inf, outf = getparam(2)
    with open(inf, "r") as ins:
        array = []
        for line in ins:
            cand = line.rstrip('\n')
            array.append("# %s" % cand)
            for char in [chr(0x5c), '(', ')', '.', '[', ']', '^', '$', "{", "}", "|", "?", "+", "*"]:
                cand = cand.replace(char, chr(0x5c) + char)
            cand = cand.lower()
            newcand = ""
            for char in cand:
                if char in string.ascii_lowercase:
                    char = '[%s%s]' % (char, char.upper())
                newcand = newcand + char
            array.append(newcand)
    f = open(outf, "w")
    f.write("\n".join(array))
    f.close()

if __name__ == '__main__':
    main()
