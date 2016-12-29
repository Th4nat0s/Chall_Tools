#!/usr/bin/env python
# coding=utf-8
import re
import sys
import json

'''
Convert the output of dir /S /R /A to Json object
For the "pooooor" responders... :)

>>>> From file sources :

 Volume in drive C has no label.
 Volume Serial Number is C4C3-B82E

 Directory of C:\Users\john

07/04/2016  11:32    <DIR>          .
07/04/2016  11:32    <DIR>          ..
05/04/2016  15:44            85�720 -!RecOveR!-aqkkg++.Png

>>>> To Json file

{
  "name": "-!RecOveR!-aqkkg++.Png",
  "time": "15:44",
  "date": "05/04/2016",
  "path": "C:\\Users\\dpc",
  "type": "file",
  "size": "85720"
}

*** Search examples :

Chercher exactement desktop.ini
./dir2warn.py output.txt | jq '.[] | select(.name == "desktop.ini")'

Cherche tous les dll et exe
./dir2warn.py output.txt | jq '.[] | select(.name | endswith(".dll",".exe")  )

Chercher un .js avec pdf dedans
./dir2warn.py output.txt | jq '.[] | select(.name | endswith(".js") and contains("pdf")  )'

'''


# Functions
def getparam(count):
    if len(sys.argv) != count + 1:
        print 'Find someting in user listing'
        print 'To Use: ' + sys.argv[0] + ' mydiroutput'
        sys.exit(1)
    else:
        return sys.argv[1]


def toutf(data):
    return data.decode('iso-8859-1').encode('utf8')


rgx_file = r'^(?P<date>\d{2}\/\d{2}\/\d{4})  (?P<time>\d{2}:\d{2}).* (?P<size>[\dÿ]+)(?P<name>.*)$'
rgx_fold = r'^ Directory of (?P<name>.*)$'
rgx_dire = r'^(?P<date>\d{2}\/\d{2}\/\d{4})  (?P<time>\d{2}:\d{2})    <DIR>(?P<name>.*)$'
rgx_link = r'^(?P<date>\d{2}\/\d{2}\/\d{4})  (?P<time>\d{2}:\d{2})    <JUNCTION>(?P<name>.*)\[(?P<link>.*)\]$'


# Main Code #####
def main():
    filename = getparam(1)
    txt = open(filename)
    txt = toutf(txt.read())  # Now contains UTF strings
    txt = txt.split('\n')  # Now contains array of line
    files = []
    curr_fold = ""
    for line in txt:
        sline = re.match(rgx_file, line.rstrip('\r'))
        if sline:  # Found a File
            size = sline.group('size').replace("ÿ", "")
            files.append({'name': sline.group('name').strip(' '), 'path': curr_fold, 'date': sline.group('date'),
                          'time': sline.group('time'), 'type': 'file', 'size': size})
        else:
            sline = re.match(rgx_fold, line.rstrip('\r'))
            if sline:  # Found a Folder lin e
                curr_fold = sline.group('name')
            else:  # Seek for a Folder item
                sline = re.match(rgx_dire, line.rstrip('\r'))
                if sline:  # Store only "." Folders
                    if sline.group('name').strip(' ') == ".":
                        files.append({'name': sline.group('name').strip(' '), 'path': curr_fold,
                                      'date': sline.group('date'), 'time': sline.group('time'), 'type': 'dir'})
                else:
                    sline = re.match(rgx_link, line.rstrip('\r'))
                    if sline:  # Found a link
                        files.append({'name': sline.group('name').strip(' '), 'path': curr_fold,
                                      'date': sline.group('date'), 'time': sline.group('time'),
                                      'type': 'link', 'link': sline.group('link')})

    print (json.dumps(files))

if __name__ == '__main__':
    main()
