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


I = 0
while I <= FILESIZE:
  open('temp.dat','wb').write(FILEARRAY[I:FILESIZE])
  STATUS, FILERESULT = commands.getstatusoutput ("file -b temp.dat" )
  if not FILERESULT == 'data':
    print ('%.8X %s') % (I ,FILERESULT )
    sys.stdout.flush()
  I += 1
