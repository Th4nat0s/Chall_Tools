#!/usr/bin/env python3
# coding=utf-8
import sys
import subprocess
import os

body = """#!/usr/bin/env python3
# coding=utf-8
import sys


# Functions
def getparam(count):
    \"\"\"Retrieve the parameters appended \"\"\"
    if len(sys.argv) != count + 1:
        print('My command')
        print('To Use: %s my params' % sys.argv[0])
        sys.exit(1)
    else:
        return sys.argv[1]


# Main Code #####
def main():
    param = getparam(1)
    print(param)

if __name__ == '__main__':
    main()
"""

if len(sys.argv) != 2:
    print ('Error, i need a script name')
    sys.exit(1)

filename = sys.argv[1]+".py"
if os.path.exists(filename):
    print ('Error, this script already exists')
    sys.exit(1)


text_file = open(filename, "w")
text_file.write(body)
text_file.close()
subprocess.call(["chmod", "+x", filename])
