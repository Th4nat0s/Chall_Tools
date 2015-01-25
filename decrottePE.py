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

def decrotte(filearray):
  dumped = False
  print ("Canditates:"),
  sys.stdout.flush()
  for M in range(0,len(filearray)-1):
    if int(filearray[M]) == ord('M') and  int(filearray[M+1]) == ord('Z') :
      print ("%d," % M),
      sys.stdout.flush()
      try:
        PE = pefile.PE(data="".join(chr(b) for b in filearray[M::]))
        for section in PE.sections:    # va chercher les data la dernierse section fait fois
          location = section.PointerToRawData
          locationadd = section.SizeOfRawData
        Z = location + locationadd
        with open(('PE_%d.exe' % M), 'w') as outfile:
            outfile.write(filearray[M:M+Z])
            dumped = True
        print ('\n[!] \tFound PE_%d.exe %d bytes saved\n\tContinue scan; ' % (M,Z)),
      except:
        pass
  print "EOF"
  return dumped


def xor(key, filearray):
  filearrayout = filearray
  for I in range (1,len(filearrayout)): # Pas 0, s'occuppe pas de l'exe host
    filearrayout[I] = filearrayout[I] ^ key
  return filearrayout

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
print "[*] Scanning %s" % FILENAME
with open(FILENAME, 'rb') as f:
  filearray = bytearray(f.read())

result = decrotte(filearray)
if result:
  sys.exit(0)

print("[!] No PE found, will try the chinese style; SIMPLE XOR")
key = 1
while key < 256:
  print ("[*] Try with xor key %d :" % key),
  result = decrotte(xor(key,filearray))
  if result:
    sys.exit(0)
  key = key+1
