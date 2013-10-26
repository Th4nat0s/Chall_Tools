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
      strings.append(lines)

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
  
  
print wtupple




