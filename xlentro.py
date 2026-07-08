#!/usr/bin/env python3
import sys
import math

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 


def shan(stin, pkey):
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
    print('KEYSIZE:', pkey, end=' ')
    print('BIT:', end=' ')
    print(int(math.ceil(fent)), end=' ')
    print('SE:', end=' ')
    print(fent)
    return fent

if len(sys.argv) != 2:
	print('Find lenght of the xor key using shannon entropy')
	print('To Use: '+ sys.argv[0]+  ' filename')
	sys.exit()
file = open(sys.argv[1], 'rb')
filename = sys.argv[1]
byteArr = bytearray(file.read())
file.close()
fileSize = len(byteArr)


maxkeylen=33
if fileSize < 33:
	maxkeylen=fileSize

for keylen in range (1,maxkeylen):
	index = 0
	st=''
	for byte in range(0, fileSize // keylen):
		st = st + chr(byteArr[index])
		index = index + keylen
	shan(st,keylen)
