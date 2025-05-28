#!/usr/bin/env python3

# v 0.3 - Python 3 adaptation
# Copyleft Thanat0s - http://Thanat0s.trollprod.org
# Licence GNU GPL

import sys

# --- Vérification des arguments ---
if len(sys.argv) != 2:
    print('Extract PHP code from a file')
    print(f'To use: {sys.argv[0]} infile')
    sys.exit(1)

# --- Lecture du fichier binaire ---
with open(sys.argv[1], 'rb') as f:
    byte_arr = bytearray(f.read())

file_size = len(byte_arr)

# --- Initialisation des variables ---
result = ''
pen_down = False
in_string = False
string_char = b''

i = 0
while i < file_size:
    byte = byte_arr[i:i+1]

    # Détection de l'entrée ou sortie de chaîne (' ou ")
    if byte in (b"'", b'"'):
        if not in_string:
            in_string = True
            string_char = byte
        elif string_char == byte:
            in_string = False
            string_char = b''

    # Hors d'une chaîne
    if not in_string:
        if byte == b"<" and i + 1 < file_size and byte_arr[i+1:i+2] == b"?":
            pen_down = True
        elif byte == b"?" and i + 1 < file_size and byte_arr[i+1:i+2] == b">":
            pen_down = False
            result += "?>"
            i += 2
            continue

    # Collecte si entre <? et ?>
    if pen_down:
        result += byte.decode('latin1')  # pour garder les caractères non-UTF8

    i += 1

# --- Affichage du résultat ---
print(result)
