#!/usr/bin/python
import sys

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 


if len(sys.argv) != 3:
	print 'To Use: cprint.py (path/filename) collenght'
	print '  ex : cprint.py myfile 15'
	sys.exit()

file = open(sys.argv[1], 'rb')
filename = sys.argv[1]
byteArr = bytearray(file.read())
file.close()
fileSize = len(byteArr)

index=0
keylen=int(sys.argv[2])
result = ""
resultp = keylen
for byte in range( 0, fileSize   ):
		mychar = byteArr[byte]  
		if mychar <= 32:
			mychar = 32
			resultp = resultp-1 
		if mychar >= 127:
			mychar = 32
			resultp = resultp-1 
		result = result + chr(mychar)
		index = index + 1
		if index == keylen:
			index = 0
			print result
			resultp = keylen
			result = ""	
