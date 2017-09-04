#!/bin/bash
disitool.py extract $1 pkcs7_$1.der
openssl pkcs7 -in pkcs7_$1.der -inform DER -print_certs -noout -text
