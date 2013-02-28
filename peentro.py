#!/usr/bin/python

import hashlib
import pefile
import math
import sys, os

# Analyse PE Section entropy
# v 0.1

# Need https://code.google.com/p/pefile

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

def shan(stin):
        fstList = list(stin)
        falphabet = list(set(fstList))
        ffreqList = []
        for fsymbol in falphabet:
                fctr = 0
                for fsym in fstList:
                        if fsym == fsymbol:
                                fctr += 1
                ffreqList.append(float(fctr) / len(fstList))
        fent = 0.0
        for ffreq in ffreqList:
                fent = fent + ffreq * math.log(ffreq, 2)
        fent = -fent
        return (fent)


SECTIONS = ['.text', '.bss', '.rdata', '.data', '.rsrc', '.edata', '.idata', '.pdata', '.debug', '.tls', '.reloc']

# Needs two arg if not... help
if len(sys.argv) != 2:
        print 'Compute the entropy of PE sections'
        print 'To Use: '+ sys.argv[0]+  ' filename'
        sys.exit(1)

FILENAME = sys.argv[1]

# Test if file exists
if not os.path.isfile(FILENAME):
    print 'File not found'
    sys.exit(2)

# Load an get sectiors
try:
  PE =  pefile.PE(FILENAME)
except:
  print "Error in loading " + FILENAME
  sys.exit(3)

print "Section\tEntropy\tBytes\tMD5\t\t\t\t\tRemark"
for section in PE.sections:
  ENTROPY = shan(section.data) 
  SECTION_USUAL = "Unusual Name."
  SECTION_NAME = str(section.Name).replace('\0','')
  for names in SECTIONS:
    if names==SECTION_NAME:
      SECTION_USUAL = ""
  if ENTROPY > 6.8:
    SECTION_USUAL = SECTION_USUAL + " High Entropy"
  print "%s\t%.2f\t%s\t%s\t%s" % ( SECTION_NAME , ENTROPY , int(math.ceil(ENTROPY)), hashlib.md5(section.data).hexdigest(),SECTION_USUAL ) 
  
