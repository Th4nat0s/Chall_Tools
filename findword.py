#!/usr/bin/env python3

# v 0.2 - Python 3 adaptation

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

# Need
# sudo apt install wfrench

import re
import sys
import unicodedata

def remove_accents(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: script.py <letters> <length>")
        sys.exit(1)

    candidates = []

    letters, length = sys.argv[1], int(sys.argv[2])
    column = (80 - length) // length  # integer division

    lettercount = []
    for char in "".join([c for i, c in enumerate(letters) if i == letters.find(c)]):
        lettercount.append([char, letters.count(char)])

    regex = re.compile("^[" + letters + "]{" + str(length) + "}$")

    with open('/usr/share/dict/french', 'r', encoding='utf-8') as f:
        for line in f:
            word = remove_accents(line.strip())
            if regex.match(word):
                linletcount = []
                for char in "".join([c for i, c in enumerate(word) if i == word.find(c)]):
                    linletcount.append([char, word.count(char)])

                invalid = False
                for letterC in linletcount:
                    for letterS in lettercount:
                        if letterS[0] == letterC[0]:
                            if letterS[1] < letterC[1]:
                                invalid = True

                if not invalid:
                    candidates.append(word)

    for i, candidate in enumerate(candidates, 1):
        print(candidate, end=' ')
        if i % column == 0:
            print("\n")
