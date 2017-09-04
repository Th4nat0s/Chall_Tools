#!/bin/bash
strings $1 -n6 > $1_TMP
strings -el $1 -n6 >> $1_TMP
cat $1_TMP | sort | uniq  > strings_$1
rm $1_TMP
