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


def find_first(number):
	for items in result:
		if items[0] <= number:
			return (items)


if len(sys.argv) < 2:
	print'  Will find all static numeric values'
	print 'very usefull for a rop add eax,[ebx-xxxxxx]'
	print ' ex : ropval.py mybinary 0xb8a0008 | sort -n'
	sys.exit()

file = open(sys.argv[1], 'rb')
filename = sys.argv[1]
byteArr = bytearray(file.read())
file.close()
filesize = len(byteArr)

print "- Loaded " + str(filesize) + " Bytes"
sys.stdout.flush()
print "- Elfread "
sys.stdout.flush()

if len(sys.argv) >= 3:
	offset=int(sys.argv[2],16)
else:
	offset=0


# Find all mapped section in elf (thank's to readelf)
elf=[]
import subprocess
cmd = subprocess.Popen('readelf -S '+sys.argv[1], shell=True, stdout=subprocess.PIPE)
for line in cmd.stdout:
	match = re.match(r'.* (AX|A) ', line)
	if match:
#		print line.rstrip()
		regex = re.search(r']\s\S+\s+\S+\s+([0-9a-f]{8})\s([0-9a-f]{6})\s([0-9a-f]{6})',line)
		if regex:
			# Stock  OFFSET, LEN, MAPPING
			elf.append([int(regex.group(2),16),int(regex.group(3),16),int(regex.group(1),16)])

print "- Finding values"
sys.stdout.flush()
result= []

# Fetch all possible values from elf sections
for section in elf:
	j = 0
	for i in range(section[0],section[0]+section[1]-4):
		potential = byteArr[i+0] +( byteArr[i+1] << 8) + (byteArr[i+2] << 16  )+ (byteArr[i+3] << 24)
		found = False
		for items in result:
			if int(potential) == items[0]:
				found = True
				break
		if not found:
			result.append ( [int(potential), section[2]+j ])	
		j = j+1

result.sort()

if len(sys.argv) == 5:
	print "Find a way from "+ sys.argv[3] + " to " + sys.argv[4],
	SRC = int(sys.argv[3],16)
	DST = int(sys.argv[4],16)
	if DST > SRC:
		GAP = DST-SRC
	else:
		GAP = 0xFFFFFFFF - SRC + DST + 1
	print "Gap is " + hex(GAP)
	result.reverse()
	SOLUTION= []
	print "solution :"+ str(GAP)+" sub(",
	while GAP <> 0:
		# hopefully 1 is alway present
		CANDIDATE = find_first(GAP)
		SOLUTION.append (CANDIDATE)
		GAP = GAP - CANDIDATE[0]
	for items in SOLUTION:
		print str(items[0]),
	print ")"
	print "memory location :",
	for items in SOLUTION:
		print '%08X' % int(items[1]) + ",",
	print ""
	print "memory offset (" + str(offset) + ") :",
	for items in SOLUTION:	
		print '"%08X"' % int(int(items[1]+offset) % 0xffffffff) + "," ,
	print ""

else:
	print "Decval","Hexval","mOffset",
	if offset<>0:
		print "sOffest"
	else:
		print ""

	for items in result:
		print str(items[0]),
		print '%08X' % items[0] ,
		print '%08X' % int(items[1]),
		if offset<>0:
			print '%08X' % int(int(items[1]+offset) % 0xffffffff),
		print ""



		
