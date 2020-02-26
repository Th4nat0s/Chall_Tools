#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage $0 AS1000"
  exit
fi

whois -h whois.radb.net -- "-i origin $1" | grep 'route:' | rev | cut -f 1 -d " " | rev | sort -u
