#!/bin/bash

# ntfs_attr.sh - Display or change attributes on an NTFS filesystem

# Tools required:
# getfattr(1) and setfattr(1)
# http://savannah.nongnu.org/projects/attr/
# (In Debian/Ubuntu: sudo apt-get install attr)
# ntfs-3g (pre-installed in most Linux distros)
# http://www.tuxera.com/community/ntfs-3g-download/

# Options (intentionally) not implemented:
# /S (search and process files of matching pattern in all subdirectories)
# /D (also process directories when used together with /S)
# Note that this is not 'recursion' switch found in most Unix utilities.
# Use find(1) together with this script instead.

# -----------------------------------------------------------------------------
# Copyright (C) 2015-2016,2018 Kang-Che Sung <explorer09 @ gmail.com>

# The MIT License (MIT)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------

# References:
# Entended attributes in ntfs-3g
# http://www.tuxera.com/community/ntfs-3g-advanced/extended-attributes/
# NTFS File Attribute Constants
# https://msdn.microsoft.com/en-us/library/windows/desktop/gg258117(v=vs.85).aspx

# Attribute values: 0 (don't change), + (set), - (clear)
attr_r=0
attr_h=0
attr_s=0
attr_a=0
attr_t=0 # Changeable in ntfs-3g. Never worked with Windows's attrib.
attr_c=0 # Changeable only in Recovery Console and not in normal Windows.
attr_o=0 # Changeable in Windows 10, version 1703 or later.
attr_i=0 # Changeable in Windows Vista or later.
# 'X' (No scrub) is changeable in attrib in Windows 8.
# 'P' (Pinned) and 'U' (Unpinned) are introduced in Windows 10, version 1703,
# and changeable in attrib there. They correspond to OneDrive "always available
# files" and "online-only files" respectively and are shown as OneDrive status
# icons in Status column in Explorer.

# The 'Not content indexed' attribute is displayed as 'N' instead of 'I' in
# Explorer in Windows Vista (bug, fixed in Windows 7):
# http://superuser.com/questions/516709

# FILE_ATTRIBUTE_DEVICE is shown as 'X' in Explorer (in Windows 7 or later),
# even though the bit is never supposed to be set on files. Panda USB Vaccine
# was known to exploit this bit for its "vaccinate" feature.
# http://superuser.com/questions/180306
# http://stackoverflow.com/questions/8617639

# Mode 'show' or 'edit' attributes
attr_mode=show

# '--no-dereference' flag
attr_no_deref=""

# Debug options.
# Show hex value of 'system.ntfs_attrib_be' when listing attributes.
attr_show_hex=""

show_usage () {
cat << USAGE
Usage: $0 [+r|-r] [+h|-h] [+s|-s] [+a|-a] [+c|-c] [+i|-i] [-L] files...
Display or change attributes on an NTFS filesystem.

  -L, --no-dereference  affect symbolic links instead of referenced files

Attributes: ( ! = unchangeable with this utility )
  r - Read-only
  h - Hidden
  s - System
  v ! Volume label (obsolete in NTFS and must not be set)
  d ! Directory
  a - Archive
  x ! Device (reserved by system and must not be set)
  n ! Normal (i.e. no other attributes set)
  t - Temporary
  p ! Sparse file
  l ! Symbolic link / Junction / Mount point / has a reparse point
  c - Compressed (flag changeable with directories only)
  o - Offline
  i - Not content indexed (shown as 'N' in Explorer in Windows Vista)
  e ! Encrypted
  V ! Integrity (for ReFS volume only; attribute not shown in Explorer)
  X ! No scrub (for ReFS volume only; attribute not shown in Explorer)
  P ! Pinned (OneDrive "always available files")
  U ! Unpinned (OneDrive "online-only files")
USAGE
}
# Order of attribute letters in "%~a1" output: "drahscotl-x"
# ('x' = No scrub. One slot is unknown; tell me if you discovered what it is.)
# Order of attribute letters in 'attrib' output: "A  SHR OI VX P U  "
# ('V' = Integrity, 'X' = No scrub, 'P' = Pinned. Eight slots are unknown.)

# If a file has a FILE_ATTRIBUTE_DEVICE set (for example an autorun.inf created
# by Panda USB Vaccine), then the "%~a1" method will refuse to show the
# attribute of the file while 'attrib' can show it, ignoring the DEVICE
# attribute bit.

while [ "$#" -ge 1 ]; do
    case "$1" in
        [+-][Rr]) attr_r=${1%[Rr]} attr_mode=edit ;;
        [+-][Hh]) attr_h=${1%[Hh]} attr_mode=edit ;;
        [+-][Ss]) attr_s=${1%[Ss]} attr_mode=edit ;;
        [+-][Aa]) attr_a=${1%[Aa]} attr_mode=edit ;;
        [+-][Tt]) attr_t=${1%[Tt]} attr_mode=edit ;;
        [+-][Cc]) attr_c=${1%[Cc]} attr_mode=edit ;;
        [+-][Oo]) attr_o=${1%[Oo]} attr_mode=edit ;;
        [+-][Ii]) attr_i=${1%[Ii]} attr_mode=edit ;;
        -L|--no-dereference)
            # This was the '/L' option in 'attrib' in Windows, however '/' is
            # path separator in Unix so we implement as '-L' instead.
            # {get,set}fattr supports '-h' for '--no-dereference' but this
            # option can be confusing in this script.
            attr_no_deref=--no-dereference
            ;;
        -?|--help)
            show_usage
            exit 0
            ;;
        *) break ;;
    esac
    shift
done

# Silently ignore the "--" option.
[ "X$1" = "X--" ] && shift

if [ "$#" -le 0 ]; then
    if [ "$attr_mode" = show ]; then
        # Default to list attributes of all files in current directory.
        exec "$0" $attr_no_deref *
    else
        echo "$0: no file specified" >&2
        exit 1
    fi
fi

attr_exit_status=0

# Process each file
for f in "$@"; do
    # getfattr bug: If argument is symlink to directory and without '-h',
    # attributes of *directory contents* will be shown as well as target
    # directory itself. (setfattr is not affected and so is safe.)
    if getfattr $attr_no_deref -e hex -n system.ntfs_attrib_be "$f" >/dev/null; then
        :
    else
        attr_exit_status=$?
        continue
    fi
    attr_hex=$(getfattr $attr_no_deref -e hex -n system.ntfs_attrib_be "$f" 2>/dev/null |
        sed '/system\.ntfs_attrib_be=/ { s/^[^0]*0[Xx]/0x/; q }; d')
    [ "$attr_show_hex" ] && printf '%s ' "$attr_hex"
    if [ "$attr_mode" = show ]; then
        attr_mask=0x1
        # Attribute that are reserved and never have letters:
        # FILE_ATTRIBUTE_VIRTUAL (0x10000)
        # FILE_ATTRIBUTE_RECALL_ON_OPEN (0x40000)
        # 0x200000
        # FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS (0x400000)
        for i in r h s v d a x n t p l c o i e V + X + P U + +; do
            if [ $(($attr_hex & $attr_mask)) -gt 0 ]; then
                printf '%c' "$i"
            else
                printf '-'
            fi
            attr_mask=$(($attr_mask*2))
        done
        printf ' %s\n' "$f"
    else
        [ "$attr_r" = "+" ] && attr_hex=$(($attr_hex |     0x1))
        [ "$attr_r" = "-" ] && attr_hex=$(($attr_hex &    ~0x1))
        [ "$attr_h" = "+" ] && attr_hex=$(($attr_hex |     0x2))
        [ "$attr_h" = "-" ] && attr_hex=$(($attr_hex &    ~0x2))
        [ "$attr_s" = "+" ] && attr_hex=$(($attr_hex |     0x4))
        [ "$attr_s" = "-" ] && attr_hex=$(($attr_hex &    ~0x4))
        [ "$attr_a" = "+" ] && attr_hex=$(($attr_hex |    0x20))
        [ "$attr_a" = "-" ] && attr_hex=$(($attr_hex &   ~0x20))
        [ "$attr_t" = "+" ] && attr_hex=$(($attr_hex |   0x100))
        [ "$attr_t" = "-" ] && attr_hex=$(($attr_hex &  ~0x100))
        if [ -d "$f" ]; then
            [ "$attr_c" = "+" ] && attr_hex=$(($attr_hex |  0x800))
            [ "$attr_c" = "-" ] && attr_hex=$(($attr_hex & ~0x800))
        fi
        [ "$attr_o" = "+" ] && attr_hex=$(($attr_hex |  0x1000))
        [ "$attr_o" = "-" ] && attr_hex=$(($attr_hex & ~0x1000))
        [ "$attr_i" = "+" ] && attr_hex=$(($attr_hex |  0x2000))
        [ "$attr_i" = "-" ] && attr_hex=$(($attr_hex & ~0x2000))
        attr_hex=$(printf '%#010x' "$attr_hex")
        setfattr $attr_no_deref -v "$attr_hex" -n system.ntfs_attrib_be "$f" ||
            attr_exit_status=$?
    fi
done

exit $attr_exit_status
