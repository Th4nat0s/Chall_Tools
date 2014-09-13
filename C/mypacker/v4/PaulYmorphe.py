#!/usr/bin/python
import random,sys,re

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

def loadfile(LFFILE):
  FILE = open(LFFILE, 'rb')
  LFARRAY = []
  for LINE in FILE:
    LFARRAY.append( LINE )
  FILE.close()
  return LFARRAY

R32 = "(E(AX|BC|CX|DX|SP|BP)"
R16 = "(AX|BX|CX|DX|SP|BP)"
R8 =  "([A-D](L|H)"
RULES = [ [["xor (R32),(R32)","mov (R32),0"],["mov (R32),0"]]
  ]

# Global variables
CODE = []
IDX = 0
CALLJMP = 0

# mov registre + immed
def O_MOV_R32_I(REG,IMMED):
  TIR = random.randrange(0,3)
  if (TIR== 0): 
    return ("mov %s,0x%X" % (REG,IMMED))
  elif (TIR == 1):
    return ("lea %s,[0x%X]" % (REG,IMMED))
  elif (TIR == 2):
    return ("push dword 0x%X\npop %s" % (IMMED,REG))

def O_CALL(ADDR):
  global CALLJMP
  CALLJMP = CALLJMP + 1
  TIR = random.randrange(0,2)
  if ( TIR == 0):
    return ("push dword .clljmp_%d\njmp %s\n.clljmp_%d:" % (CALLJMP,ADDR,CALLJMP))
  elif ( TIR == 1): 
    return ("call %s" % (ADDR))


def O_XOR(REG):
  #XorREGwithREG;testReturn 
  TIR = random.randrange(0,2)
  if ( TIR == 0): 
    return (O_MOV_R32_I(REG,0)) 
  elif ( TIR == 1): 
    return ("xor %s,%s" % (REG,REG))

def O_INC(REG):
  #XorREGwithREG;testReturn 
  randome.seed(REG)
  TIR = random.randrange(0,2)
  if ( TIR == 0): 
    return ("inc %s"%REG) 
  elif ( TIR == 1): 
    return ("add %s,1" % REG) 

def O_DEC(REG):
  #XorREGwithREG;testReturn 
  TIR = random.randrange(0,2)
  if ( TIR == 0): 
    return ("dec %s" % REG) 
  elif ( TIR == 1): 
    return ("sub %s,1" % REG) 

def O_LOOP(ADDR):
  #XorREGwithREG;testReturn 
  TIR = random.randrange(0,2)
  if ( TIR == 0): 
    return ("loop %s" % REG) 
  elif ( TIR == 1): 
    return ("%s\njnz %s" % (O_DEC("ECX"),ADDR)) 


if __name__ == '__main__':

  if len(sys.argv) != 2:
	  print 'PolyMorph Asm Source file'
	  print 'To Use: ' + sys.argv[0] + ' infile'
	  sys.exit()

  BUFFER = []
  BUFFER = loadfile(sys.argv[1])
  CODE = [] 

  # Remove empty, clean up, remove comments and macro ref
  for LINES in BUFFER:
    LINES = LINES.replace("\t"," ")
    LINES = LINES.split(";")[0]
    LINES = " ".join(LINES.split())
    LINES = LINES.rstrip("\n")
    if not re.match("%line ", LINES):
      if not LINES == "":
        CODE.append(LINES) 
        #1print "+"+LINES+"+"

  rREG32 = "((:?E[ABCD]X)|(:?E[SD]I)|EBP|ESP)"
  rREG16 = "((:?[ABCD]X)|(:?[SD]I)|BP|SP)"
  rREG8 = "((:?[ABCD][HL])"

  for IDX in range(0,len(CODE)):
    if re.match(r"(\.\S+:\s)?MOV\s+"+rREG32+",\d+", CODE[IDX], flags=re.IGNORECASE): 
      RGX = re.search(r"\s(.*),(.*)(:?\s|$)",CODE[IDX])
      REG = RGX.group(1)
      IMMED = int(RGX.group(2))
      CODE[IDX] = O_MOV_R32_I(REG,IMMED)  
    if re.match(r"xor\s+((:?e[abcd]x)|(:?E[SD]I)|EBP|ESP),\1", CODE[IDX], flags=re.IGNORECASE): 
      REG = re.search(r"\s(.*),",CODE[IDX]).group(1)
      CODE[IDX] = O_XOR(REG)  
    if re.match(r"dec\s+"+rREG32+"(\s|$)" , CODE[IDX], flags=re.IGNORECASE):
      REG = re.search(r"\s(.*)(\s|$)",CODE[IDX]).group(1)
      CODE[IDX] = O_DEC(REG)
    if re.match(r"inc\s+"+rREG32+"(\s|$)" , CODE[IDX], flags=re.IGNORECASE):
      REG = re.search(r"\s(.*)(\s|$)",CODE[IDX]).group(1)
      CODE[IDX] = O_INC(REG)
    if re.match(r"call\s" , CODE[IDX], flags=re.IGNORECASE):
      ADDR = re.search(r"\s(.*)(\s|$)",CODE[IDX]).group(1)
      CODE[IDX] = O_CALL(ADDR)
    if re.match(r"loop\s" , CODE[IDX], flags=re.IGNORECASE):
      ADDR = re.search(r"\s(.*)(\s|$)",CODE[IDX]).group(1)
      CODE[IDX] = O_LOOP(ADDR)
    print CODE[IDX] 
