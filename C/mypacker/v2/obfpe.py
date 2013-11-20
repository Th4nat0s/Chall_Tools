#!/usr/bin/python
import random
import sys
import struct

if __name__ == '__main__':
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
  dosstub=bytearray()
  IDX=0
  dospay = 0xb8,0x00,0x4c,0xcd,0x21
  for I in range(0,0x40):
    dosstub[I:I+1] = payload[I:I+1]
    IDX=IDX+1
  for I in ( dospay ):  # mov ax,0x4c00; Int 0x21
    dosstub.append(I)
    IDX=IDX+1
  for I in range(0,64 - len (dospay)):
    dosstub.append(0x00)
    IDX=IDX+1
  for I in range(IDX,payload_len):
    dosstub[I:I+1] = payload[I:I+1]

  # Choisis une taille de BBOX de 128 a 256 bytes
  bboxlen = random.randrange(128)+128
  print ('** BBox Len: %d' % bboxlen)

  # Genere le BBox Array
  
  bboxarray=[]
  for i in range(0,bboxlen):
    bboxarray.append(i)
  random.shuffle(bboxarray)

  #print bboxarray

  fullrow = payload_len // bboxlen 
  restrow = payload_len % bboxlen

  print ('* Process %dx%d bytes row and %d bytes' % (fullrow,bboxlen,restrow)) 
  
  opayload = []
  
  for BBraw in range(0,fullrow):
    for I in bboxarray:
      opayload.append(payload[(BBraw*bboxlen)+I])

  for J in range(0,restrow):
      I = bboxarray[J]
      opayload.append(payload[(BBraw*bboxlen)+I])
  
  out = bytearray(opayload)
  out = dosstub
  with open(sys.argv[1]+'.bin',"w") as f:
    f.write(out)

  
