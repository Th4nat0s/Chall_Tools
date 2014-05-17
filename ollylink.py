#!/usr/bin/env python
# coding=utf-8   

# Script for IDAPYTHON for importing API CAll name.
# c Thanat0s 2014.

# Relink Module library export from ollydbg to IDA f

#  To get source : ollydbg > View Executable Name > Show Name in all module > Copy Whole table

import re, sys

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'Fit OllyDbg export into Ida references'
    print 'To Use: '+ sys.argv[0]+  ' olly_function_export.txt'
    sys.exit(1)
  else:
    return sys.argv[1]

# Main Code #####
regxport = r'^(?P<offset>[A-F\d]+)\s+[\d\w]+(?:\s+|>)Export\s+#\d+\s+(?P<function>[\d\w]+)'

def main():
  functnum = 0
  functions = {}
  f = open('c:\\temp\\export.txt','r')
  # f = open(getparam(1),'r')
  for line in f.readlines():
    candidate = re.search(regxport, line)
    if candidate:
      functnum = functnum + 1
      functions['0x' + str.lower(candidate.group('offset'))] = candidate.group('function')  # Format 0xba2345678
  print('[+] Loaded %d DLL functions' % functnum)

  functnum = 0
  ea = ScreenEA()  # EA = Offset@Mouse
  ida_function = []  
  ida_offset = {}
  for function_ea in Functions(SegStart(ea), SegEnd(ea)): # liste les fonctions
    functnum = functnum + 1
    ida_function.append(function_ea)
    for addresse in Heads(function_ea,FindFuncEnd(function_ea)):
      for offset in DataRefsFrom(addresse): 
        ida_offset[(offset)] = offset  
  print('[+] IDA Got %d Data Ref in %d Subfunctions in Seg %x' % (len(ida_offset), functnum, SegStart(ea)))
  
  functnum = 0
  functfound = 0
  for offset in ida_offset:
    if re.match(r'^dword_',Name(offset)):
      functnum = functnum + 1
      if hex(Dword(offset)) in functions: 
        MakeName(offset,functions[hex(Dword(offset))])
	functfound = functfound + 1
	#print Name(offset),hex(offset),hex(Dword(offset)), 'found'
  print('[+] Find %d Api call out of %d unknown ref' % (functfound, functnum))

if __name__ == '__main__':
  main()
