#!/usr/bin/python
import sys

# v 0.2

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

# Extract "Correctly" PHP Code from file

if len(sys.argv) != 2:
	print 'Extract PHP Code from a file'
	print 'To Use: ' + sys.argv[0] + ' infile'
	sys.exit()

file = open(sys.argv[1], 'rb')
byteArr = bytearray(file.read())
file.close()
fileSize = len(byteArr)

Result = ''
PenDown = False
Comment = False
CommentType = ''
for byte in range( 0, fileSize ):
	# Ignore <? et ?> dans les strings
	if ((byteArr[byte] == ord("'")) and (CommentType == '' or CommentType == ord("'"))): 
		Comment = not Comment # Toggle True to False
		if Comment == True:
			CommentType = "'"
		else:
			CommentType = ''

	# Ignore <? et ?> dans les strings
	if ((byteArr[byte] == ord('"')) and (CommentType == '' or CommentType == ord('"'))): 
		Comment = not Comment # Toggle True to False
		if Comment == True:   
			CommentType = '"'
		else:
			CommentType = ''

	# Prend entre  <? et ?> 
	if Comment == False:
		if (byteArr[byte] == ord("<")) and (byteArr[byte+1] == ord("?")) :
			PenDown = True
		if (byteArr[byte] == ord("?")) and (byteArr[byte+1] == ord(">")) :
			PenDown = False
			Result = Result + chr(byteArr[byte]) + chr(byteArr[byte+1])

	if PenDown == True: 
		Result = Result + chr(byteArr[byte])
	
print Result
