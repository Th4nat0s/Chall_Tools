#!/usr/bin/python

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

import sys
from subprocess import call
import os
import re

if len(sys.argv) != 2:
    print 'To Use: '+ sys.argv[0]+' elffilename'
		print 'Will find all static numeric values'
		print 'very usefull for a rop mov eax,[ebx]'

    sys.exit()
file = open(sys.argv[1], 'rb')
filename = sys.argv[1]
byteArr = bytearray(file.read())
file.close()
filesize = len(byteArr)

#print "- Loaded " + str(filesize) + " Bytes"
sys.stdout.flush()
#print "- Elfread "
sys.stdout.flush()


elf=[]
import subprocess
cmd = subprocess.Popen('readelf -S '+sys.argv[1], shell=True, stdout=subprocess.PIPE)
for line in cmd.stdout:
	match = re.match(r'.* (AX|A|WA) ', line)
	if match:
#		print line.rstrip()
		regex = re.search(r']\s\S+\s+\S+\s+([0-9a-f]{8})\s([0-9a-f]{6})\s([0-9a-f]{6})',line)
		if regex:
			# Stock  OFFSET, LEN, MAPPING
			elf.append([int(regex.group(2),16),int(regex.group(3),16),int(regex.group(1),16)])

print "- Finding values"
result= []


for section in elf:
	j = 0
	for i in range(section[0],section[0]+section[1]-4):
		potential = byteArr[i+0] +( byteArr[i+1] << 8) + (byteArr[i+2] << 16  )+ (byteArr[i+3] << 24)
		found = False
		for items in result:
			if int(potential) == items[0]:
				found = True
		if not found:
			result.append ( [int(potential), section[2]+j ])	
		j = j+1

print "Decval","Hexval","Offset"
for items in result:
	print str(items[0]),
	print '%08X' % items[0] ,
	print '%08X' % int(items[1])

