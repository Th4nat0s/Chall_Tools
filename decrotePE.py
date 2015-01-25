#!/usr/bin/python

import pefile
import sys, os

# Extract PE File
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
if len(sys.argv) != 2:
        print 'Extract PE from Dump'
        print 'To Use: '+ sys.argv[0]+  ' filename'
        sys.exit(1)
FILENAME = sys.argv[1]

# Test if file exists
if not os.path.isfile(FILENAME):
    print 'File not found'
    sys.exit(1)

with open(FILENAME, 'rb') as f:
  filearray = bytearray(f.read())

for M in range(0,len(filearray)-1):
  if int(filearray[M]) == ord('M') and  int(filearray[M+1]) == ord('Z') :
    print ("Candidate Found at offset %d" % M),
    try:
      PE = pefile.PE(data="".join(chr(b) for b in filearray[M::]))
      for section in PE.sections:
        location = section.PointerToRawData
        locationadd = section.SizeOfRawData
      Z = location + locationadd
      with open(('PE_%d.exe' % M), 'w') as outfile:
          outfile.write(filearray[M:M+Z])
      print ('PE_%d.exe %d bytes saved' % (M,(M+Z-M)))
    except:
      print "False positive"
