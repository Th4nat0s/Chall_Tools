#!/usr/bin/python

import pefile
import sys, os

# Xor a file with "strin" key.
# v 0.1

# Need https://code.google.com/p/pefile et on lui doit TOUT
#

# Extract PEFile from "Dump"
#

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

# Needs two arg if not... help
if len(sys.argv) <= 2:
        print 'Xor a file with Byte key'
        print 'To Use: '+ sys.argv[0]+  ' filename xorkey '
        print '  xorkey is a strning'
        sys.exit(1)

FILENAME = sys.argv[1]

# Test if file exists
if not os.path.isfile(FILENAME):
    print 'ERROR: File not found'
    sys.exit(1)

INC = 0
# Get xor key
KEYS = sys.argv[2]

print "data, key, inc, base, result"
LINE=0
PK = 0
with open(FILENAME, 'rb') as f:
    filearray = bytearray(f.read())
    for I in range(0, len(filearray)):
        BCK = int(filearray[I])
        KEY = ord(KEYS[PK % len(KEYS)])
        PK = PK + 1
        filearray[I] = (filearray[I] ^ KEY) % 255

        LINE =LINE+1
        if LINE < 10:
            print (int(BCK), KEY, INC, int(filearray[I]))
        if LINE == 11:
            print "... "

print ('writing output to %s.xor' % FILENAME)
with open(('%s.xor' % FILENAME), 'w') as outfile:
  outfile.write(filearray)
