#!/usr/bin/env python
# coding=utf-8   
import sys,subprocess,os

body =  """#!/usr/bin/env python
# coding=utf-8   
import re, sys

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'My command'
    print 'To Use: '+ sys.argv[0]+  ' my params'
    sys.exit(1)
  else:
    return sys.argv[1]

# Main Code #####
def main():
  param = getparam(1)


if __name__ == '__main__':
  main()
"""

if len(sys.argv) != 2:
  print 'Error, i need a script name'
  sys.exit(1)

filename = sys.argv[1]+".py"
if os.path.exists(filename):
  print 'Error, this script already exists'
  sys.exit(1)


text_file = open(filename, "w")
text_file.write(body)
text_file.close()
subprocess.call(["chmod", "+x", filename] )
