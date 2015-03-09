#!/usr/bin/env python
# coding=utf-8   
import re, sys, random, string



#Dim vaLFVutQ As Integer^M
#vaLFVutQ = 3^M
#Do While vaLFVutQ < 32^M
#DoEvents: vaLFVutQ = vaLFVutQ + 1^M
#Loop^M

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'Machouille Macro'
    print 'Obfuscate VBA macro .. To Use: '+ sys.argv[0]+  ' filename'
    sys.exit(1)
  else:
    return sys.argv[1]

# Main Code #####
def decoy():
  N = 8 
  param = getparam(1)
  NAME = ''.join(random.choice(string.letters + string.digits) for _ in range(N))
  NUM = random.randrange(64)
  body = ("\nDim %s As Integer\n" % NAME)
  body += ("%s = %d\n" % (NAME, NUM))
  body += ("Do While %s < %d\n" % (NAME, NUM + random.randrange(64)))
  body += ("DoEvents: %s = %s + 1\n" % (NAME,NAME))
  body += ("Loop\n\n")
  return body

def main():
  mfile = getparam(1)
  f = open(mfile, 'rb')
  for line in f.readlines():
    print line
    print decoy()



if __name__ == '__main__':
  main()
