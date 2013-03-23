#!/usr/bin/python
import sys

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 


"""
Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .text         00020eb4  00401000  00401000  00000400  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  1 .data         00000400  00422000  00422000  00021400  2**2
                  CONTENTS, ALLOC, LOAD, DATA
  2 .reloc        00001692  00425000  00425000  00021800  2**2
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
"""

filename='facture.unpack.exe'
offset = 0x400
array = 0x00402C80
base = 0x00401000

file = open(filename, 'rb')
byteArr = bytearray(file.read())
file.close()
fileSize = len(byteArr)

index = 0
stringcount = 0

while True:
  lena = byteArr[array - base + offset + index ]
  lenb = byteArr[array - base + offset + 1 + index]
  lenc = byteArr[array - base + offset + 2 + index]
  lend = byteArr[array - base + offset + 3 + index]
  offa = byteArr[array - base + offset + 4 + index]
  offb = byteArr[array - base + offset + 5 + index]
  offc = byteArr[array - base + offset + 6 + index]
  offd = byteArr[array - base + offset + 7 + index]

  if (offa+offb+offc+offd == 0):
    break

  print ('Str:%02x Len:%02x%02x Key:%02x%02x Off:%02x%02x%02x%02x') % (stringcount, lend,lenc,lenb,lena, offd,offc,offb,offa),
  index = index + 8
  stringcount = stringcount + 1
  strlen = ( lend << 8 ) + lenc
  key = lena
  stringoff = ( offd << 24 ) + ( offc << 16) + ( offb << 8) +  offa
  decoded = ''
  i = 0
  j = 0
  while (i < strlen):
    decoded = decoded + chr(((byteArr[stringoff - base + offset + i ] ^ key) % 256) ^ j ) 
    i = i + 1
    j = (j+ 1 ) % 256

  print decoded
