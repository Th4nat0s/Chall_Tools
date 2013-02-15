#!/usr/bin/python
import sys
import re
import base64
import zlib
import codecs

# v 0.2 Beta de Beta de chez Beta

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

# Extract Php Code from obfuscated
# Understand :
#		base64
#		bzinflate
#   eval
#   rot13
#   string reverse 

func_payload = ''
phpoutput = '' 
CRLF  = chr(0x0a)
EVALCOUNT = 0

# print debug messages
def debug(str_debug,crlf_debug = False):
	if crlf_debug:
		print str_debug , 
	else:
		print str_debug

# remove quotes around a string ' and "
def decoted(str_decote):
	str_decote = re.sub('(\"|\')$', '', str_decote)
	str_decote = re.sub('^(\"|\')', '', str_decote)
	return str_decote



# Evaluate php functions
def evaluate(strline):
	global phpoutput
	global PHP_Variable
	global func_payload
	global EVALCOUNT
	
	# Variable settings
	if re.match('^\$' ,strline):
		variable = re.split('=', strline, 1)
		debug("Set variable : " + variable[0]) 
		PHP_Variable[variable[0]]= variable[1]
	 	phpoutput = phpoutput + strline + "; " + CRLF

	# Eval()	
	elif re.match('^eval(\s)*\(.*\)' ,strline):
		debug ( "Fonction eval " , 1)
		code_regex = re.match(r"^eval(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		if not re.match('^(\'|\"|\$)',code ):
			debug (", Sub" , 1)
			evaluate(code)
		else:
			func_payload = code
		EVALCOUNT = EVALCOUNT + 1
		phpoutput = phpoutput + "// DECODING EVALCOUNT " + str(EVALCOUNT) + CRLF
		phpoutput = phpoutput + func_payload + ";" + CRLF
		func_payload ="" 

	# gzinflate()
	elif re.match("^gzinflate(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^gzinflate(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		debug ( "Function gzinflate " , 1 )
		if not re.match('^(\'|\"|\$)',code ):
			debug ( ", Sub", 1 )
			evaluate(code)
		# No more nested function
		if re.match('^\$', code):  # gzinflate variable
			func_payload = PHP_Variable[code] # from previous set variable
		elif re.match('^(\'|\")',code ): # else load from direct code
			func_payload = code
		func_payload = zlib.decompressobj().decompress('x\x9c' + func_payload)

	# base64_decode
	elif re.match("^base64_decode(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^base64_decode(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		debug ( "Function base64_decode " , 1 )
		if not re.match('^(\'|\"|\$)',code ):
			debug (", Sub", 1 )
			evaluate(code)
		# No more nested function
		if re.match('^\$', code): 
			func_payload =PHP_Variable[code] # from previous set variable
		elif re.match('^(\'|\")',code ): # else load from direct code
			func_payload = code
		func_payload = base64.b64decode(decoted(func_payload))
		debug ( "Done")

	# str_rot13
	elif re.match("^str_rot13(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^str_rot13(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		debug ( "Function str_rot13 " , 1 )
		# Test for nested function
		if not re.match('^(\'|\"|\$)',code ):
			debug ( ", Sub", 1 )
			evaluate(code)
		# No nested function load value, 
		if re.match('^\$', code):  # if value is a variable
			func_payload = decoted( PHP_Variable[code]) # from previous set variable
		elif re.match('^(\'|\")',code ): # else load from direct code
			func_payload = code
		# if not a variable or quoted, it's from a previous function
		func_payload =  codecs.encode( decoted(func_payload), "rot13" )

	# strrev	
	elif re.match("^strrev(\s)*\((?P<CODE>.*)\)", strline):
		code_regex = re.match(r"^strrev(\s)*\((?P<CODE>.*)\)", strline)
		code = code_regex.group('CODE')
		debug ("Function strrev"  , 1 )
		if not re.match('^(\'|\"|\$)',code ):
			debug( ", Sub", 1 )
			evaluate(code)
  	# No more nested function
		if re.match('^\$', code):  # gzinflate variabl
			func_payload = PHP_Variable[code] # from previous set variable
		elif re.match('^(\'|\")',code ):
			func_payload = code
		func_payload =  decoted(func_payload[::-1])
	
	# Any other lines are only registered
	else:
		debug ( "Unknown sentence : " + strline )
		phpoutput = phpoutput + strline 
		if re.search(r'\{(\s)*$',strline ):
			phpoutput = phpoutput  + CRLF
		else:	
			phpoutput = phpoutput + ";"+ CRLF

if len(sys.argv) != 2:
	print 'Deobfuscate PHP Code from a file'
	print 'To Use: ' + sys.argv[0] + ' infile'
	sys.exit()


# open File
file = open(sys.argv[1], 'rb')
byteArr = bytearray(file.read())
file.close()
fileSize = len(byteArr)

# How many eval found
EVALFOUND = len(re.findall(r"eval(\s)*\(",byteArr ) ) 

if EVALFOUND == 0 :
	debug ("No Eval() found, quitting " )
	sys.exit()
else:
	debug ("Eval() found: " + str(EVALFOUND))


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

	# Prend le code entre  <? et ?> 
	if Comment == False:
		if (byteArr[byte] == ord("<")) and (byteArr[byte+1] == ord("?")) and (byteArr[byte+2] == ord("p")) and (byteArr[byte+3] == ord("h")) and (byteArr[byte+4] == ord("p"))  :
			PenDown = True
			byte = byte + 5
			if  (byte >= fileSize-1):
				break
	
		if (byteArr[byte] == ord("<")) and (byteArr[byte+1] == ord("?")) :
			PenDown = True
			byte = byte + 2
			if  (byte >= fileSize-1):
				break


		if (byteArr[byte] == ord("?")) and (byteArr[byte+1] == ord(">")) :
			PenDown = False
			byte = byte + 2
			if  (byte >= fileSize-1):
			        break
										

		# CRLF on ; 
		if (byteArr[byte] == ord(";")) :
			Result = Result + chr(0x0a) 
			byte = byte + 1
			if  (byte >= fileSize-1):
				break
	
		# if blabla {  }
		if (byteArr[byte] == ord("{")) :
			Result = Result +  "{" + chr(0x0a)
			byte = byte + 1
			if  (byte >= fileSize-1):
				break

		if (byteArr[byte] == 0x0d ) :
			byte = byte + 1
	 		if  (byte >= fileSize-1):
				break
					
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
		if tmpbuffer != "":
			line.append ( tmpbuffer)
		tmpbuffer = ''
	tmpbuffer = tmpbuffer + char


phpoutput = "<?php" + CRLF
phpoutput = phpoutput + "// Decoded by phpeval.py" + CRLF
# phpoutput = phpoutput + "// DECODING EVALCOUNT " + str(EVALCOUNT) + CRLF
PHP_Variable={}
for strline in line:
	evaluate(strline)
phpoutput = phpoutput + "// END OF DECODING EVALCOUNT " + str(EVALCOUNT) + CRLF
phpoutput = phpoutput + "?>" + CRLF

# output 
print phpoutput
