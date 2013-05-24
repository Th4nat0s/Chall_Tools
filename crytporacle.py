#!/usr/bin/python

# v 0.1

# Copyleft Thanat0s
# http://Thanat0s.trollprod.org
#
# Licence GNU GPL



import struct
import sys


CONSTANTES = [
[ 'AES constantes',   [ 0x00000001, 0x00000002, 0x00000004, 0x00000008,
                        0x00000010, 0x00000020, 0x00000040, 0x00000080,
                        0x0000001B, 0x00000036 ]],
[ 'AES Reverse SBox', [ 0xD56A0952, 0x38A53630, 0x9EA340BF, 0xFBD7F381,
                        0x8239E37C, 0x87FF2F9B, 0x44438E34, 0xCBE9DEC4,
                        0x32947B54, 0x3D23C2A6, 0x0B954CEE, 0x4EC3FA42,
                        0x66A12E08, 0xB224D928, 0x49A25B76, 0x25D18B6D,
                        0x64F6F872, 0x16986886, 0xCC5CA4D4, 0x92B6655D,
                        0x5048706C, 0xDAB9EDFD, 0x5746155E, 0x849D8DA7,
                        0x00ABD890, 0x0AD3BC8C, 0x0558E4F7, 0x0645B3B8,
                        0x8F1E2CD0, 0x020F3FCA, 0x03BDAFC1, 0x6B8A1301,
0x4111913A, 0xEADC674F, 0xCECFF297, 0x73E6B4F0,
0x2274AC96, 0x8535ADE7, 0xE837F9E2, 0x6EDF751C,
0x711AF147, 0x89C5291D, 0x0E62B76F, 0x1BBE18AA,
0x4B3E56FC, 0x2079D2C6, 0xFEC0DB9A, 0xF45ACD78,
0x33A8DD1F, 0x31C70788, 0x591012B1, 0x5FEC8027,
0xA97F5160, 0x0D4AB519, 0x9F7AE52D, 0xEF9CC993,
0x4D3BE0A0, 0xB0F52AAE, 0x3CBBEBC8, 0x61995383,
0x7E042B17, 0x26D677BA, 0x631469E1, 0x7D0C2155 ]],
  

[ 'SHA1 constantes',  [ 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476,
                        0xC3D2E1F0, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC,
                        0xCA62C1D6]],
[ 'MD4/5 constantes R', [ 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476 ]],
[ 'MD5 constantes K', [ 0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
                        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
                        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
                        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
                        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
                        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
                        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
                        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
                        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
                        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
                        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
                        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
                        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
                        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
                        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
                        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391 ]],
['Whirpool Hash SBox', [ 0xE8C62318, 0x4F01B887, 0xF5D2A636, 0x52916F79,
                          0x8E9BBC60, 0x357B0CA3, 0xC2D7E01D, 0x57FE4B2E,
                        0xE5377715, 0xDA4AF09F, 0x0A29C958, 0x856BA0B1,
                        0xF4105DBD, 0x67053ECB, 0x8B4127E4, 0xD8957DA7,
                        0x667CEEFB, 0x9E4717DD, 0x07BF2DCA, 0x33835AAD,
                        0x71AA0263, 0xD94919C8, 0x885BE3F2, 0xB032269A,
     0x80D50FE9, 0x4834CDBE, 0x5F907AFF, 0xAE1A6820,
0x229354B4, 0x1273F164, 0xECC30840, 0x3D8DA1DB,
0x2BCF0097, 0x1BD68276, 0x506AAFB5, 0xEF30F345,
0xEAA2553F, 0xC02FBA65, 0x4DFD1CDE, 0x8A067592,
0x1F0EE6B2, 0x96A8D462, 0x5925C5F9, 0x4C397284,
0x8C38785E, 0x61E2A5D1, 0x1E9C21B3, 0x04FCC743,
0x0D6D9951, 0x247EDFFA, 0x11CEAB3B, 0xEBB74E8F,
0xF794813C, 0xD32C13B9, 0x03C46EE7, 0xA97F4456,
0x53C1BB2A, 0x6C9D0BDC, 0x46F67431, 0xE11489AC,
0x09693A16, 0xEDD0B670, 0xA49842CC, 0x86F85C28 ]]

]


if __name__ == '__main__':

  if len(sys.argv) < 2:
    print 'Find cryto remarquables values in file'
    print 'Examples:'
    print sys.argv[0] + ' myexefile'
    sys.exit()


  fromfile = sys.argv[1]

  with open(fromfile, 'rb') as f:
    filearray = bytearray(f.read())

  for CONST in CONSTANTES:
    print 'Checking ' + CONST[0],
    VALCOUNT = 0
    VALFOUND = 0
    for VALUES in CONST[1]:  # Test AABBCCDD
      VALCOUNT = VALCOUNT + 1
      for I in range (0, len(filearray) - 8):
        DWORD = struct.unpack('L',str(filearray[I:I+4]))[0]
        if DWORD == VALUES:
          VALFOUND = VALFOUND + 1
          break
    if VALFOUND <> VALCOUNT:      # We have not Found IT... byteswap
      VALCOUNT = 0
      VALFOUND = 0
      for VALUES in CONST[1]:
        VALCOUNT = VALCOUNT + 1
        val = 0
        for i,n in enumerate(range(4)):
          d = VALUES & 0xFF
          val |= (d << (8 * (4 - i - 1)))
          VALUES >>= 8
        VALUES = val
        for I in range (0, len(filearray) - 8):
          DWORD = struct.unpack('L',str(filearray[I:I+4]))[0]
          if DWORD == VALUES:
            VALFOUND = VALFOUND + 1
            break
    print ' Found ' + str( ( VALFOUND * 100) / VALCOUNT ) + '%' 
