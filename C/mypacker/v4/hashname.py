#!/usr/bin/python
import random

STRINGS = [ 'LdrEnumResources','Sleep', 'ntdll.dll', 'kernel32.dll', 'VirtualAlloc',"NtResumeThread","WriteProcessMemory","GetThreadContext",
            "SetThreadContext","NtUnmapViewOfSection","GetProcAddress","CreateProcessA","GetLastError",
            "VirtualAllocEx","ReadProcessMemory","LoadLibrary","ResumeThread"]

def ROR(x, n,bits=32):
    mask = (2L**n) - 1
    mask_bits = x & mask
    return (x >> n) | (mask_bits << (32 - n))

def ROL(x, n, bits=32):
    return ROR(x, bits - n, bits)

HASH_SFT = random.randrange(30)+1
include = ('HASH_SFT equ 0x%X\n' % (HASH_SFT))  

for ITEMS in STRINGS:
  code=0
  for char in ITEMS.upper():
    code = code ^ ord(char)
    code = ROL(code , HASH_SFT)
  include = include +  ('HASH_%s equ 0x%X\n' % (ITEMS.upper(),code))  

print "* Hashing strings"
print include
with open('hashs.inc', 'w') as f:
  f.write(include)
