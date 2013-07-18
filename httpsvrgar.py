#!/usr/bin/python

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

# A file 2 "basic" Socket Webserver...
import socket
import re
import sys

if __name__ == '__main__':


  HOST = None               # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port

  if len(sys.argv) < 2:
    print 'Serve a file.. This file should have headers and body'
    print 'Examples:'
    print ' - serve itself ' + sys.argv[0] + './' + sys.argv[0] 
    sys.exit()


  fromfile  = sys.argv[1]
  print ( 'I will serve %s on port %d' ) % (fromfile,PORT )

  with open(fromfile, 'rb') as f:
    filearray = f.readlines()


  s = None
  for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break

  if s is None:
    print 'could not open socket'
    sys.exit(1)
  conn, addr = s.accept()
  print 'Connected by', addr
  while 1:
    data = conn.recv(1024)
    if not data: 
      break
    else:
      if re.match('^GET ', data):
        print ('Received %s' ) % (data)
        for lines in filearray:
          conn.send(lines)
  conn.close()
