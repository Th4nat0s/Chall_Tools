#!/usr/bin/env python3
import sys
import ipaddress

def summarize_ip_file(file_path):
    try:
        with open(file_path, 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

    # Convert to ip_address objects
    try:
        ip_objs = [ipaddress.ip_address(ip) for ip in ips]
    except ValueError as e:
        print(f"Invalid IP detected: {e}")
        sys.exit(1)

    ip_objs.sort()
    cidrs = ipaddress.collapse_addresses(ip_objs)

    for c in cidrs:
        print(c)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python summarize_cidr.py <ip_list.txt>")
        sys.exit(1)
    summarize_ip_file(sys.argv[1])

