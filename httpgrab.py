#!/usr/bin/env python
# coding=utf-8   

# Doc : http://thanat0s.trollprod.org/2015/04/firefox-en-console-cest-mieux-que-lynx/
import  sys,os
from selenium import webdriver

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'My command'
    print 'To Use: '+ sys.argv[0]+  ' my params'
    sys.exit(1)
  else:
    return sys.argv[1],sys.argv[2]

# Main Code #####
def main():
  page, name = getparam(2)
  print ("get %s to %s" % (page,name))
  print ("Start FFox")
  seleniumobj = webdriver.Firefox()
  print ("Get Page")
  seleniumobj.get(page)
  print ("Save Page")
  seleniumobj.save_screenshot(name)
  seleniumobj.quit()


if __name__ == '__main__':
  main()
