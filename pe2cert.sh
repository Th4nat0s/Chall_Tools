#!/bin/bash
if [ -e "$1" ]; then
  disitool.py extract $1 pkcs7_$1.der 2>/dev/null
  if [ $? -eq 0 ]; then
    openssl pkcs7 -in pkcs7_$1.der -inform DER -print_certs > x509_$1.pem
    openssl x509 -noout -fingerprint -md5 -inform pem -in x509_$1.pem > cert_$1.txt
    openssl x509 -noout -fingerprint -sha1 -inform pem -in x509_$1.pem >> cert_$1.txt
    openssl x509 -noout -fingerprint -sha256 -inform pem -in x509_$1.pem >> cert_$1.txt
    openssl pkcs7 -in pkcs7_$1.der -inform DER -print_certs -noout -text >> cert_$1.txt
  else
    echo "Seems it does not contains a signature"
  fi
else
  echo "Supply a PE file as argument please"
fi
