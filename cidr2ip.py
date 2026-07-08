#!/usr/bin/env python3
import sys
import ipaddress

def cidr_to_ip_list(cidr: str) -> list[str]:
    network = ipaddress.ip_network(cidr, strict=False)
    # include network and broadcast
    return [str(ip) for ip in network]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cidr2ip.py cidr")
        sys.exit(1)
    for lines in cidr_to_ip_list(sys.argv[1]):
        print (lines)

