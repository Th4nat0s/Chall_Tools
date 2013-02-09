#!/usr/bin/python
import sys
import re
import base64
import zlib

# v 0.1 Beta de Beta de chez Beta

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

# Extract Php Code from obfuscated
# Understand :
#		base64
#		bzinflate
#   eval

func_payload = ''
phpoutput = '' 
CRLF  = chr(0x0a)
ROUND = 0

def evaluate(strline):
	global phpoutput
	global PHP_Variable
	global func_payload
	global ROUND
# Evaluate the code in a string
	if re.match('^\$' ,strline):
		variable = re.split('=', strline, 1)
		print "Set variable : " + variable[0]
		PHP_Variable[variable[0]]= variable[1]
	 	phpoutput = phpoutput + strline + "; " + CRLF

	elif re.match('^eval(\s)*\(.*\)' ,strline):
		print "Fonction eval " ,
		code_regex = re.match(r"^eval(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		if not re.match('^(\'|\"|\$)',code ):
			print ", Sub",
			evaluate(code)
		else:
			func_payload = code
		ROUND = ROUND + 1
		phpoutput = phpoutput + "// DECODING ROUND " + str(ROUND) + CRLF
		phpoutput = phpoutput + func_payload + ";" + CRLF

	elif re.match("^gzinflate(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^gzinflate(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		print "Function gzinflate " ,
		if not re.match('^(\'|\"|\$)',code ):
			print ", Sub",
			evaluate(code)
		# No more nested function
		if re.match('^\$', code):  # gzinflate variable
			func_payload = PHP_Variable[code] # from previous set variable
		#else:
			#//	func_payload = code  #
		func_payload = zlib.decompressobj().decompress('x\x9c' + func_payload)

	elif re.match("^base64_decode(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^base64_decode(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		print "Function base64_decode " ,
		if not re.match('^(\'|\"|\$)',code ):
			print ", Sub",
			evaluate(code)
		# No more nested function
		if re.match('^\$', code):  # gzinflate variable
			func_payload = PHP_Variable[code] # from previous set variable
			func_payload = re.sub('(\"|\')$', '', func_payload)
			func_payload = re.sub('^(\"|\')', '', func_payload)
		else:
			func_payload = code  
			func_payload = re.sub('^[\"\']',  '', func_payload)
			func_payload = re.sub('[\"\']$',  '', func_payload)# 
		func_payload = base64.b64decode(func_payload)
		print "Done"

	else:
		print "Unknown sentence : " + strline
		phpoutput = phpoutput + strline + ";"+ CRLF


if len(sys.argv) != 2:
	print 'Deobfuscate PHP Code from a file'
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
byte =  0

# Preproccessing .. clean UP ; 
while ( byte <= fileSize-1) :
	# Ignore dans les strings
	if ((byteArr[byte] == ord("'")) and (CommentType != '"')):
		Comment = not Comment # Toggle True to False
		if Comment == True:
			CommentType = "'"
		else:
			CommentType = ''

	# Ignore dans les strings
	if ((byteArr[byte] == ord('"')) and (CommentType != "'" )):
		Comment = not Comment # Toggle True to False
		if Comment == True:   
			CommentType = '"'
		else:
			CommentType = ''

	# Prend entre  <? et ?> 
	if Comment == False:
		if (byteArr[byte] == ord("<")) and (byteArr[byte+1] == ord("?")) and (byteArr[byte+2] == ord("p")) and (byteArr[byte+3] == ord("h")) and (byteArr[byte+4] == ord("p"))  :
			PenDown = True
			byte = byte + 5
	
		if (byteArr[byte] == ord("<")) and (byteArr[byte+1] == ord("?")) :
			PenDown = True
			byte = byte + 2

		if (byteArr[byte] == ord("?")) and (byteArr[byte+1] == ord(">")) :
			PenDown = False
			byte = byte + 2

		# CRLF on ; 
		if (byteArr[byte] == ord(";")) :
			Result = Result + chr(0x0a) 
			byte = byte + 1

		if (byteArr[byte] == 0x0d ) :
			byte = byte + 1

	if PenDown == True:
		Result = Result + chr(byteArr[byte])
	byte = byte + 1


line = []
byte = 0
tmpbuffer = '' 
# Convert Array to strings
for char in Result:
	if char == chr(0x0A) :
	  # Chomp line	
		tmpbuffer = tmpbuffer.rstrip('\n')
		tmpbuffer = re.sub('\s+',	 ' ', tmpbuffer)
		tmpbuffer = re.sub('^\s',	 '', tmpbuffer)
		# Comment out
		tmpbuffer = re.sub('^\/\*.*\*\/', '', tmpbuffer)
		tmpbuffer = re.sub('^\/\/.*$', '', tmpbuffer)
		if tmpbuffer != "":
			line.append ( tmpbuffer)
		tmpbuffer = ''
	tmpbuffer = tmpbuffer + char


phpoutput = phpoutput + "// Decoded by phpeval.py" + CRLF
phpoutput = phpoutput + "// DECODING ROUND " + str(ROUND) + CRLF
PHP_Variable={}
for strline in line:
	evaluate(strline)
phpoutput = phpoutput + "// END OF DECODING ROUND " + str(ROUND) + CRLF

print phpoutput
