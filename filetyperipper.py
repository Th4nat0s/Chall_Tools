#!/usr/bin/python

import sys
import commands

try:
  import magic
except ImportError:
  print 'python-magic is not installed, file types will not be available'
  sys.exit(1)  





# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

# Needs two arg if not... help
if len(sys.argv) != 2:
        print 'Harvest and extract'
        print 'To Use: '+ sys.argv[0]+  ' filename'
        sys.exit(1)
FILE = sys.argv[1]

file = open(FILE, 'rb')
FILEARRAY = bytearray(file.read())
file.close()
FILESIZE = len(FILEARRAY)

print "loaded %s" % ( FILESIZE ) 


# Min 64 Bytes
I = FILESIZE - 64
BOUND = FILESIZE

while I > 64:
  with magic.Magic as m:
    FILERESULT = m.id_buffer(FILEARRAY[I:BOUND])
 ## open('temp.dat','wb').write(FILEARRAY[I:BOUND])
 ## STATUS, FILERESULT = commands.getstatusoutput ("file -b temp.dat" )
  if not FILERESULT == 'data':
    print ('%.8X %s') % (I ,FILERESULT )
    sys.stdout.flush()
    # If Found a file, set a new Bound (But always at least 16k)
    BOUND = I + 16000
    if BOUND > FILESIZE:
      BOUND = FILESIZE
  I -= 1
