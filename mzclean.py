#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL 

# Replacea Clean MZ Stub of PE
"""
          00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  4d 5a 90 00 03 00 00 00  04 00 00 00 ff ff 00 00  |MZ..............|
00000010  b8 00 00 00 00 00 00 00  40 00 00 00 00 00 00 00  |........@.......|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000030  00 00 00 00 00 00 00 00  00 00 00 00 d8 00 00 00  |................|
00000040  0e 1f ba 0e 00 b4 09 cd  21 b8 01 4c cd 21 54 68  |........!..L.!Th|
00000050  69 73 20 70 72 6f 67 72  61 6d 20 63 61 6e 6e 6f  |is program canno|
00000060  74 20 62 65 20 72 75 6e  20 69 6e 20 44 4f 53 20  |t be run in DOS |
00000070  6d 6f 64 65 2e 0d 0d 0a  24 00 00 00 00 00 00 00  |mode....$.......|
00000080  59 96 f6 68 1d f7 98 3b  1d f7 98 3b 1d f7 98 3b  |Y..h...;...;...;|
00000090  de f8 97 3b 1c f7 98 3b  1d f7 99 3b 27 f7 98 3b  |...;...;...;'..;|
000000a0  de f8 c5 3b 10 f7 98 3b  de f8 c6 3b 1c f7 98 3b  |...;...;...;...;|
000000b0  de f8 c7 3b 0d f7 98 3b  de f8 c2 3b 1c f7 98 3b  |...;...;...;...;|
000000c0  52 69 63 68 1d f7 98 3b  00 00 00 00 00 00 00 00  |Rich...;........|
000000d0  00 00 00 00 00 00 00 00  50 45 00 00 4c 01 03 00  |........PE..L...|

0000h                   2 char   ID='MZ' ou ZM
0002h                   1 word   Number of bytes in last 512-byte page of executable
0004h                   1 word   Total number of 512-byte pages in executable
0006h                   1 word   Number of relocation entries
0008h                   1 word   Header size in paragraphs
000Ah                   1 word   Minimum paragraphs of memory allocated in addition to the code size
000Ch                   1 word   Maximum number of paragraphs allocated in addition to the code size
000Eh                   1 word   Initial SS relative to start of executable
0010h                   1 word   Initial SP
0012h                   1 word   Checksum (or 0) of executable
0014h                   1 dword  CS:IP relative to start of executable entry point
0018h                   1 word   Offset of relocation table;
                                 40h for new-(NE,LE,LX,W3,PE etc.) executable
001Ah                   1 word   Overlay number (0h = main program)
001Ch                   4 byte   ????
0020h                   1 word   Behaviour bits ??
0022h                  26 byte   reserved (0)
003Ch                   1 dword  Offset of new executable header
00d8                    XXX Pe Start

00000000  4d 5a 6c 00 01 00 00 00  02 00 00 00 ff ff 00 00  |MZl.............|
00000010  00 00 00 00 11 00 00 00  40 00 00 00 00 00 00 00  |........@.......|
00000020  57 69 6e 33 32 20 50 72  6f 67 72 61 6d 21 0d 0a  |Win32 Program!..|
00000030  24 b4 09 ba 00 01 cd 21  b4 4c cd 21 60 00 00 00  |$......!.L.!`...|
00000040  47 6f 4c 69 6e 6b 20 77  77 77 2e 47 6f 44 65 76  |GoLink www.GoDev|
00000050  54 6f 6f 6c 2e 63 6f 6d  00 00 00 00 00 00 00 00  |Tool.com........|
00000060  50 45 00 00 4c 01 03 00  b2 10 87 52 00 00 00 00  |PE..L......R....|

"""

STUBMZ = [  0x4d, 0x5a, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00,
            0xb8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd8, 0x00, 0x00, 0x00,
            0x0e, 0x1f, 0xba, 0x0e, 0x00, 0xb4, 0x09, 0xcd, 0x21, 0xb8, 0x01, 4c, cd, 21, 54, 68,
            0x69, 0x73, 0x20, 0x70, 0x72, 0x6f, 0x67, 0x72, 0x61, 0x6d, 0x20, 63, 61, 6e, 6e, 6f,  
            0x6d, 0x6f, 0x64, 0x65 ,0x2e, 0x0d ,0x0d, 0x0a, 0x24, 0x00, 0x00 ,00 ,00 ,00, 00 ,00,
            0x59, 0x96, 0xf6, 0x68 ,0x1d, 0xf7, 0x98, 0x3b, 0x1d, 0xf7 ,0x98 ,3b ,1d ,f7 ,98 ,3b,
            0xde, 0xf8, 0x97, 0x3b, 0x1c, 0xf7, 0x98, 0x3b, 0x1d, 0xf7 ,0x99 ,3b ,27 ,f7 ,98 ,3b,
            0xde, 0xf8, 0xc5, 0x3b, 0x10, 0xf7, 0x98, 0x3b, 0xde, 0Xf8 ,0xc6 ,3b ,1c ,f7 ,98 ,3b, 
            0xde, 0xf8, 0xc7, 0x3b, 0x0d, 0xf7, 0x98, 0x3b, 0xde, 0xf8 ,0xc2 ,3b ,1c ,f7 ,98 ,3b, 
            0x52, 0x69, 0x63, 0x68, 0x1d, 0xf7, 0x98, 0x3b, 0x00, 0X00 ,0x00, 00, 00 ,00, 00, 00, 
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00


if len(sys.argv) != 2:
  print 'mzclean clean MZ headers of a PE file'
  print 'To Use: ' + sys.argv[0] + ' infile'
  sys.exit()

FILEARRAY = []
file = open(sys.argv[1], 'rb')
FILEARRAY = bytearray(file.read())
file.close()
FILESIZE = len(FILEARRAY)

print ('Loaded %d' % FILESIZE)



       
