#!/usr/bin/python
import sys
import re
import hashlib
import urllib
import time
import os

if __name__ == '__main__':

  if len(sys.argv) < 2:
    print 'Find uri and download'
    print 'Examples:'
    print '   ripurl myfile.php' 
    sys.exit()

URLRGX = r"(?:['\" ])(http[s]?:\/\/.*?)(?:[ '\"])"

with open(sys.argv[1], 'rb') as f:
 filearray = bytearray(f.read())

# Trim non printable
string = ""
CR = False
for char in range (0,len(filearray)):
  CH = filearray[char]
  if (CH>32 and CH<127):
    string = string + chr(CH)
  if (CH==0x0d or CH==0x0a or CH==0x09):
    string = string + " "

LOG = []
LOG.append ('Url Rip of %s - %s \n' % (sys.argv[1],time.strftime("%d/%m/%Y")))
CANDIDATE = []
FOUND = re.findall(URLRGX,string,re.IGNORECASE)
for URL in FOUND:
  if (URL.lower()<>"https://" and URL.lower()<>"http://"):
    CANDIDATE.append( URL)

RIPNAME = './RIPLOG-'+sys.argv[1]
if not os.path.exists(RIPNAME):
    os.makedirs(RIPNAME)

ID=0
for URI in CANDIDATE:
  MD5 =  hashlib.md5(URI).hexdigest()
  STATUS = ("%d: %s %s" % (ID,MD5,URI))
  print STATUS,
  sys.stdout.flush()
  try:
    urllib.urlretrieve (URI,RIPNAME+"/"+"RIP-"+MD5)
    print "Ok"
    STATUS = STATUS + " Ok"
  except:
    print "Failed"
    STATUS = STATUS + " Failed"
  finally:
    LOG.append(STATUS)
    ID=ID+1 

file = open(RIPNAME+'/RIPLOG-'+sys.argv[1],'w')
for LINE in LOG:
  file.write("%s\n" % LINE)
file.close()

