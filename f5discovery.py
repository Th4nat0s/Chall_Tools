#!/usr/bin/env python3

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL

# A F5 cookie dissector/finder

import re
import sys
import http.cookiejar
import urllib.request, urllib.error, urllib.parse
import struct

cookies = http.cookiejar.LWPCookieJar()
handlers = [
    urllib.request.HTTPHandler(),
    urllib.request.HTTPSHandler(),
    urllib.request.HTTPCookieProcessor(cookies)
    ]
opener = urllib.request.build_opener(*handlers)

def fetch(uri):
    req = urllib.request.Request(uri)
    return opener.open(req)

def decode(ltmcook):
    (host, port, end) = ltmcook.split('.')
    (a, b, c, d) = [ord(i) for i in struct.pack("<I", int(host))]
    p = [ord(i) for i in struct.pack("<I", int(port))]
    return str(str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)), p[0]*256 + p[1]

if __name__ == '__main__':


  if len(sys.argv) < 2:
    print('Scan for a website for a F5 LTM stickiness cookie')
    print('Examples:')
    print(sys.argv[0] + ' http://thanat0s.trollprod.org')
    sys.exit()
  
  uri = sys.argv[1]
  res = fetch(uri)
  found = False
  print('+ Search for Cookies..')
  for cookie in cookies:
    if re.match(r'^[\d]+\.[\d]+\.[\d]+$', cookie.value):
     found = True
     ip,port = decode(cookie.value) 
     print(('\t> %s Backend : %s:%s %s') % (cookie.name,ip,port,'<< Got a F5 one'))
    else:
      print(('\t> %s') % (cookie.name))

  if found:
    print('A F5 device was detected')
