#!/usr/bin/python

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL


# Big Hug to bmiseplon sur #python-fr
# This Code is clean :)

import re
import sys

if __name__ == '__main__':

  if len(sys.argv) < 2:
    print 'Replace in a file. Regex aware'
    print 'Examples:'
    print ' - Replace something but keeping a byte' + sys.argv[0] + 'mybinaryfile "\\xb8\\xa0(.)\\xff" "\\x90\\x90\\\\\\\\1\\x90"'
    print ' - Replace a string' + sys.argv[0] + 'mybinaryfile "www.toto" "www.titi"'
    print '   I Know ... 4 esc is annoying.. It\'s a quick tools'
    sys.exit()



  fromfile, frompattern, topattern = sys.argv[1:]
  tofile = '%s_patched' % fromfile
  frompattern = bytes(frompattern).decode('string-escape')
  topattern = bytes(topattern).decode('string-escape')

  with open(fromfile, 'rb') as f:
    filearray = bytearray(f.read())

  with open(tofile, 'wb') as f:
    f.write(re.sub(frompattern, topattern, filearray))

