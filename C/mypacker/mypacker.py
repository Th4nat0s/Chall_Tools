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

