#!/usr/bin/python
# Obfuscate strings in strings

import random
import sys

strings = []
fstrings = [ 'ntdll', 'kernel32',"NtResumeThread","WriteProcessMemory","GetThreadContext",
             "SetThreadContext","NtUnmapViewOfSection","GetProcAddress","CreateProcessA",
             "ReadProcessMemory","LoadLibrary","c:\\windows\\system32\\notepad.exe"]

if __name__ == '__main__':


# Load Strings Dictionnary
  with open('strings.txt', 'r') as f:
    for lines in f.readlines():
      strings.append(lines.rstrip("\n"))

wtupple=[]
# Cherche required letters
for words in fstrings:
  wsolution = [] 
  for letters in words:
    #print ("Seek for %s" % letters)
    linec=0
    solution=[]
    for lines in strings:
      linec = linec + 1
      pos = 0
      for char in lines:
        pos = pos + 1
        if (char == letters): 
          solution.append ([linec,pos])
          #print ("Found %s at pos %d in line %d" % (letters,pos,linec))
    # shuffle found solution
    wsolution.append(solution[random.randrange(len(solution))])
  wtupple.append([words, wsolution]) 

# Select unique used lines
solution=[]
i=0
for words in wtupple:
  for linec,pos in words[1]:
    found = False
    for candidate in solution:
      if candidate[0] == linec:
        found = True
    if not found:
      i = i + 1
      solution.append([linec,i])

# Write lines.
i=0;
for line in solution:
  i=i+1
  tstring=strings[line[0]-1].replace("\"","\\\"")
  tstring=tstring.replace("%","\\%")
  print ("bstr%d: db \"%s\", 0x00" % (i,tstring)) 

i=0

randrange = random.randrange(0xfffff)
print ("allstroff: dd 0x%x" % randrange) 
for line in solution:
  i=i+1
  print ("allstr%d: dd bstr%d  - 0x%x" % (i,i,randrange))

# Write stings mapping 
i=0;
for words in wtupple:
  i=i+1
  tstring=words[0].replace("\\","_")
  tstring=tstring.replace(":","_")
  print ("str_%s: db " % tstring),
  for linec,pos in words[1]:
    print ("0x%x," % pos), 
    for line in solution:
      if line[0] == linec:
        print ("0x%x," % line[1])  ,
        break
  print( "0x0; %s" % words[0])
  print ("GLOBAL str_%s" % tstring) 
