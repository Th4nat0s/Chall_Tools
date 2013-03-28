#!/usr/bin/python

import sys
import commands

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

FILE = 'image.sys'
file = open(FILE, 'rb')
FILEARRAY = bytearray(file.read())
file.close()
FILESIZE = len(FILEARRAY)

print "loaded %s" % ( FILESIZE ) 


# Min 64 Bytes
I = FILESIZE - 64
BOUND = FILESIZE

while I > 64:
  open('temp.dat','wb').write(FILEARRAY[I:BOUND])
  STATUS, FILERESULT = commands.getstatusoutput ("file -b temp.dat" )
  if not FILERESULT == 'data':
    print ('%.8X %s') % (I ,FILERESULT )
    sys.stdout.flush()
    # If Found a file, set a new Bound (But always at least 16k)
    BOUND = I + 16000
    if BOUND > FILESIZE:
      BOUND = FILESIZE
  I -= 1
