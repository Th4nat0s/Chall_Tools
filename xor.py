#!/usr/bin/python

import pefile
import sys, os

# Xor a file with byte key. 
# v 0.1

# Need https://code.google.com/p/pefile et on lui doit TOUT
#

# Extract PEFile from "Dump"
#

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

def getint(thestr):
  try:
    if "x" in thestr.lower(): # hex
      value = int(thestr.lower().split('x')[1], 16)
      if "-" in thestr.lower(): # Negatif
        value = 0-value
    else:
      value = int (thestr)
  except:
    print "ERROR Key in invalid format"
    sys.exit(1)
  return (value)


# Needs two arg if not... help
if len(sys.argv) <= 2:
        print 'Xor a file with Byte key'
        print 'To Use: '+ sys.argv[0]+  ' filename xorkey [inc|dec|number] [start]'
        print '  xorkey could be in hex(0x41) or decimal (101)'
        print '  if inc|dec the xor key will be (inc|dec) on each byte, it could be also a 8bit signed value'
        print '  if [start] start the xor key increment at this value (hex or decimal)'
        sys.exit(1)
FILENAME = sys.argv[1]

# Test if file exists
if not os.path.isfile(FILENAME):
    print 'ERROR: File not found'
    sys.exit(1)

INC = 0
# Get arg 3
if len(sys.argv) >= 3+1:
  if sys.argv[3] == "inc".lower():
    INC = 1
  elif sys.argv[3] == "dec".lower():
    INC = -1
  else:
    INC = getint(sys.argv[3]) % 256

# Get xor key
KEY = getint(sys.argv[2])

BASE = 0
# Get increment value
if len(sys.argv) == 4+1:
  BASE = getint(sys.argv[4]) 

print "data, key, inc, base, result"
LINE=0
with open(FILENAME, 'rb') as f:
  filearray = bytearray(f.read())
  for I in range (0, len(filearray)):
    BCK = int( filearray[I])
    filearray[I] = (filearray[I] ^  KEY) % 256
    #KEY = (KEY + (INC + BASE)%256 ) % 256
    LINE =LINE+1
    if LINE < 10:
      print (int(BCK), KEY, INC, BASE, int( filearray[I]) )
    if LINE == 11:
      print "... "
    KEY = (KEY + INC + BASE ) % 256
    BASE = 0

print ('writing output to %s.xor' % FILENAME)
with open(('%s.xor' % FILENAME), 'w') as outfile:
  outfile.write(filearray)
