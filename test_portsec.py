#!/usr/bin/env python
# coding=utf-8   
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import random, sys
from scapy.all import srp,sr1,IP,ICMP,Ether

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'My command'
    print 'To Use: '+ sys.argv[0]+  ' ipv4toping'
    sys.exit(1)
  else:
    return sys.argv[1]

def macr():
    random.seed()
    return ((":%x") % random.randrange(0,0xff))

# Main Code #####
def main():
  param = getparam(1)
  ping =  Ether() / IP(dst=param) / ICMP()
  if ping['Ethernet'].dst=="ff:ff:ff:ff:ff:ff":
    print "It seems that the host did'nt answer to arp"
    sys.exit(1)
  print ("Ready to sent icmp to %s @ %s" % (ping['Ethernet'].dst, ping['IP'].dst))
  print "Pinging with real MAC...",
  sys.stdout.flush()
  rep,non_rep = srp(ping ,timeout=5,verbose=0)
  if rep:
    print "Got answer...\nTrying with other sources"
    MAC1 = "00:0c:29"
    for I in range(2,16):
      ping =  Ether(src=MAC1+macr()+macr()+macr()) / IP(dst=param) / ICMP()
      rep,non_rep = srp(ping ,timeout=5,verbose=0)
      if rep:
        print ("%s pass; %i Mac address allowed" % (ping['Ethernet'].src, I))
      else:
        print ("Mmmm... Didn't answer anymore Security allow %i Mac" % I)
        sys.exit(1)
  else:
    print "The host did'nt answer"
    sys.exit(1)
  print "No port security in place"

if __name__ == '__main__':
  main()
