#!/usr/bin/python

import pefile
import sys, os

# Analyse PE Section entropy
# v 0.2

# Need https://code.google.com/p/pefile et on lui doit TOUT

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

SECTIONS = ['.text', '.bss', '.rdata', '.data', '.rsrc', '.edata', '.idata', '.pdata', '.debug',  '.xdata', '.reloc', '.rsrc', '.code', '.tls']

# Needs two arg if not... help
if len(sys.argv) != 2:
        print 'Compute the entropy of PE sections'
        print 'To Use: '+ sys.argv[0]+  ' filename'
        sys.exit(1)
FILENAME = sys.argv[1]

# Test if file exists
if not os.path.isfile(FILENAME):
    print 'File not found'
    sys.exit(1)

# Load an get sectiors
try:
    PE =  pefile.PE(FILENAME, fast_load=True)
except:
    print "Error in loading " + FILENAME

print "Section\t\tEntropy\t\tSize\tMD5\t\t\t\t\tRemark"
for section in PE.sections:
  ENTROPY = section.get_entropy()
  SECTION_NAME = section.Name.strip().replace(chr(0x00),"")
  REMARKS = []
  SECTION_USUAL = True
  for names in SECTIONS:
    if names==SECTION_NAME:
      SECTION_USUAL = False
  if SECTION_USUAL:
    REMARKS.append ( "Unusal Segment" )
  if ENTROPY > 7:
    REMARKS.append ( "High Entropy" )
  print ("%s%s\t%s\t%s\t%s\t%s" % (SECTION_NAME ,' '*(8-len(SECTION_NAME)) , ENTROPY, section.SizeOfRawData,   section.get_hash_md5(), ','.join(REMARKS)))
 
