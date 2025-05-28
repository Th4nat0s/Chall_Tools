#!/usr/bin/env python3

# v 0.2 - Python 3 adaptation

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL
# Big Hug to bmiseplon sur #python-fr
# This Code is clean :)

import re
import sys
import codecs

def decode_escapes(s):
    return codecs.decode(s, 'unicode_escape').encode('latin1')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Replace in a file. Regex aware')
        print('Examples:')
        print(f' - Replace something but keeping a byte: {sys.argv[0]} mybinaryfile "\\\\xb8\\\\xa0(.)\\\\xff" "\\\\x90\\\\x90\\\\\\\\1\\\\x90"')
        print(f' - Replace a string: {sys.argv[0]} mybinaryfile "www.toto" "www.titi"')
        print("   I Know ... 4 esc is annoying.. It's a quick tool")
        sys.exit(1)

    fromfile, frompattern, topattern = sys.argv[1], sys.argv[2], sys.argv[3]
    tofile = f'{fromfile}_patched'

    # Decode the escape sequences into raw bytes
    frompattern_bytes = decode_escapes(frompattern)
    topattern_bytes = decode_escapes(topattern)

    with open(fromfile, 'rb') as f:
        filearray = f.read()

    patched = re.sub(frompattern_bytes, topattern_bytes, filearray)

    with open(tofile, 'wb') as f:
        f.write(patched)


