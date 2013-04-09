#!/usr/bin/python

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL


# Big Hug to bmiseplon sur #python-fr
#This Code is clean :)

import re
import sys
import string
import unicodedata
 
def removeAccentedChars(s):
  u = unicode( s, "utf-8" )
  return unicodedata.normalize('NFKD',u).encode('ascii','ignore')
      

letters = "mechant"
length = 7 

pattern = "^["+ letters + "]{" + str(length) + "}$"

if __name__ == '__main__':

  letters, length = sys.argv[1:]
  length = int(length)


  lettercount = []

  for char in "".join([c for i,c in enumerate(letters) if i==letters.find(c)]):
    lettercount.append( [char, letters.count(char)])

  regex = re.compile ("^["+ letters + "]{" + str(length) + "}$")
  
  with open('/usr/share/dict/french', 'r') as f:
    for lines in f.readlines():
      lines = removeAccentedChars(lines).rstrip() # Remove crlf and accents
      if regex.match(lines):  # find candidate with the regex
        linletcount = []   # Count the letters in the candidate.
        for char in "".join([c for i,c in enumerate(lines) if i==lines.find(c)]):
            linletcount.append( [char, lines.count(char)])

        invalid = False
        for letterC in linletcount:   # Pour Chaque source
          for letterS in lettercount:  # Pour chaque dest 
            if letterS[0]  == letterC[0]: # trouve la lettre...
              if letterS[1] > letterC[1]: # y a t'il le meme nombre de letttres
                invalid = True
 
        if invalid == False:
          print lines
