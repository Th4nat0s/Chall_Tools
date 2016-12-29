#!/usr/bin/env python
# coding=utf-8
import re
import sys


# Functions
def getparam(count):
    if len(sys.argv) != count + 1:
        print 'My command'
        print 'To Use: ' + sys.argv[0] + ' my params'
        sys.exit(1)
    else:
        return sys.argv[1]


class no_bcolors:
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    OKNUMBER = ''
    WARNING = ''
    ENDC = ''
    FAIL = ''


class txt_bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKNUMBER = '\033[90m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    FAIL = '\033[91m'


class html_bcolors:
    HEADER = '<span style="color:OrangeRed">'
    OKBLUE = '<span style="color:MediumPurple">'
    OKGREEN = '<span style="color:Lime">'
    OKNUMBER = '<span style="color:Yellow">'
    WARNING = '<span style="color:Red ">'
    FAIL = '<span style="color:DeepPink; background-color:Yellow;">'
    ENDC = '</span>'


def nocomments(txtarr):
    # Parses LINES
    output = []
    for line in txtarr:
        # Remove ' something except in "'"
        line = re.sub("(?P<quoted>((?<=\")?)'(?(1)(?!\")).*$)", "", line)
        if not re.match(r'^(\s+)?$', line):
            if not re.match(r'^Attribute VB_', line):  # Remove attribute declarations
                output.append(line.strip(' \t\n\r'))

    return output


def chrprint(val):
    val = int("%s" % val.group(1))
    if val in xrange(32, 127):
        return "\"" + chr(val) + "\""
    else:
        return "Chr$(" + ("%d" % val) + ")"


def chrconcat(val):
    return "\"" + val.group(1) + val.group(3) + "\""


def nochr(txtarr):
    output = []
    for line in txtarr:
        line = re.sub(r'Chr\$\s?\(\s?(\d+)\s?\)', chrprint, line)  # convert chr(xx) to "x"
        while re.findall(r'\"(\S+)\"\s?(\&|\+)\s?\"(\S+)\"', line):  # convent "b" + "b" to "bb"
            line = re.sub(r'\"(\S+)\"\s?(\&|\+)\s?\"(\S+)\"', chrconcat, line)
        output.append(line)
    return(output)


def nowrap(txtarr):
    output = []
    line = ""
    for i in xrange(0, len(txtarr)):
        if re.findall(r'_$', txtarr[i]):
            line = line + " " + re.sub(r'_$', '', txtarr[i]).strip(' ')
        else:
            if line != "":
                line = line + " " + txtarr[i]
                while re.findall(r'  ', line):
                    line = re.sub(r'  ', ' ', line)
                line = line.strip(' ')
            else:
                line = txtarr[i]
            output.append(line)
            line = ""
    return(output)


def tabit(txtarr, otype):
    tab = 0
    ident = 4  # Size of tab
    output = []
    tabchar = " "
    if otype == "HTML":
        tabchar = "&nbsp;"
    for line in txtarr:
        tabbed = 0
        if re.match('With |Select |(Private Sub |Sub |(Public )?Function |For |If |Do$|Else$)', line):
            tab += ident
            tabbed = ident
        if re.match('(!Select) Case |(End (Function|Sub|Select|With)|Else($| )|End If$|Next($| )|Loop$)', line):
            tab -= ident

        # Special case one line
        if re.match('(If .* Then .*$)', line):
            tabbed = 0
            tab -= ident

        output.append("%s%s" % (tabchar*(tab-tabbed), line))

        # Special case endfunction
        if re.match('(End Function|End Sub)', line):
            tab = 0  # FIXUP !! in case of
            output.append("")
    return(output)


def colorit(txtarr, otype):
    bcolors = txt_bcolors
    output = []

    if otype == "HTML":
        output.append('<div style="width:100%"><code style="background-color:black; color:white">')
        bcolors = html_bcolors
    commands = [["End Function", bcolors.HEADER, bcolors.ENDC],
                ["Function", bcolors.HEADER, bcolors.ENDC],
                ["End Sub", bcolors.HEADER, bcolors.ENDC],

                ["Private Sub", bcolors.HEADER, bcolors.ENDC],
                ["Sub", bcolors.HEADER, bcolors.ENDC],

                ["End If", bcolors.OKGREEN, bcolors.ENDC],
                ["To", bcolors.OKGREEN, bcolors.ENDC],
                ["Next", bcolors.OKGREEN, bcolors.ENDC],
                ["Then", bcolors.OKGREEN, bcolors.ENDC],
                ["Else", bcolors.OKGREEN, bcolors.ENDC],
                ["Error", bcolors.OKGREEN, bcolors.ENDC],
                ["Dim", bcolors.OKGREEN, bcolors.ENDC],
                ["For", bcolors.OKGREEN, bcolors.ENDC],
                ["Do", bcolors.OKGREEN, bcolors.ENDC],
                ["Loop", bcolors.OKGREEN, bcolors.ENDC],
                ["If", bcolors.OKGREEN, bcolors.ENDC],
                ["GoTo", bcolors.OKGREEN, bcolors.ENDC],
                ["Exit", bcolors.OKGREEN, bcolors.ENDC],
                ["MsgBox", bcolors.OKGREEN, bcolors.ENDC],
                ["InStr", bcolors.OKGREEN, bcolors.ENDC],
                ["Not", bcolors.OKGREEN, bcolors.ENDC],
                ["Set", bcolors.OKGREEN, bcolors.ENDC],
                ["New", bcolors.OKGREEN, bcolors.ENDC],
                ["IsNumeric", bcolors.OKGREEN, bcolors.ENDC],
                ["Format", bcolors.OKGREEN, bcolors.ENDC],
                ["Select", bcolors.OKGREEN, bcolors.ENDC],
                ["Case", bcolors.OKGREEN, bcolors.ENDC],
                ["Trim", bcolors.OKGREEN, bcolors.ENDC],
                ["RTrim", bcolors.OKGREEN, bcolors.ENDC],
                ["LTrim", bcolors.OKGREEN, bcolors.ENDC],
                ["Replace", bcolors.OKGREEN, bcolors.ENDC],
                ["Select", bcolors.OKGREEN, bcolors.ENDC],
                ["Case", bcolors.OKGREEN, bcolors.ENDC],
                ["With", bcolors.OKGREEN, bcolors.ENDC],
                ["Public", bcolors.OKGREEN, bcolors.ENDC],
                ["Keycode", bcolors.OKGREEN, bcolors.ENDC],
                ["SendKeys", bcolors.OKGREEN, bcolors.ENDC],

                ["Debug.Print", bcolors.FAIL, bcolors.ENDC],
                ["Document.Open", bcolors.FAIL, bcolors.ENDC],
                ["Shell", bcolors.FAIL, bcolors.ENDC],
                [".OpenTextFile", bcolors.FAIL, bcolors.ENDC],
                ["CreateObject", bcolors.FAIL, bcolors.ENDC],
                [".Open", bcolors.FAIL, bcolors.ENDC],
                ["autoopen", bcolors.FAIL, bcolors.ENDC],
                ["Environ", bcolors.FAIL, bcolors.ENDC],
                # ["Microsoft.XMLHTTP", bcolors.FAIL, bcolors.ENDC],
                # ["Scripting.FileSystemObject", bcolors.FAIL, bcolors.ENDC],
                ["Byte", bcolors.OKBLUE, bcolors.ENDC],
                ["ByVal", bcolors.OKBLUE, bcolors.ENDC],
                ["String", bcolors.OKBLUE, bcolors.ENDC],
                ["Long", bcolors.OKBLUE, bcolors.ENDC],
                ["Integer", bcolors.OKBLUE, bcolors.ENDC],
                ["Boolean", bcolors.OKBLUE, bcolors.ENDC],
                ["Variant", bcolors.OKBLUE, bcolors.ENDC],
                ["Attribute", bcolors.OKBLUE, bcolors.ENDC],
                ["True", bcolors.OKBLUE, bcolors.ENDC],
                ["False", bcolors.OKBLUE, bcolors.ENDC],
                ["Nothing", bcolors.OKBLUE, bcolors.ENDC],
                ["TextBox", bcolors.OKBLUE, bcolors.ENDC],
                ["ComboBox", bcolors.OKBLUE, bcolors.ENDC],
                ["CheckBox", bcolors.OKBLUE, bcolors.ENDC],
                ["vbExclamation", bcolors.OKBLUE, bcolors.ENDC],

                ["Optional", bcolors.OKBLUE, bcolors.ENDC],
                ["ByRef", bcolors.OKBLUE, bcolors.ENDC],
                ["ListBox", bcolors.OKBLUE, bcolors.ENDC],
                ["CommandButton", bcolors.OKBLUE, bcolors.ENDC],
                ["Image", bcolors.OKBLUE, bcolors.ENDC],
                ["ReDim", bcolors.OKGREEN, bcolors.ENDC],
                ["Mod", bcolors.OKGREEN, bcolors.ENDC],
                ["On", bcolors.OKGREEN, bcolors.ENDC],
                ["Resume", bcolors.OKGREEN, bcolors.ENDC],
                ["As", bcolors.OKGREEN, bcolors.ENDC]]

    for line in txtarr:
        line = re.sub("(\\b\\d+\\b)", bcolors.OKNUMBER + (r"\1") + bcolors.ENDC, line)
        for command in commands:
            line = re.sub("\\b((?<=\")?)("+command[0]+")(?(1)(?!\"))\\b", command[1] + command[0] + command[2], line)

        output.append(line)
        if otype == "HTML":
            output.append('<br>')

    if otype == "HTML":
        output.append('</code></div>')
    return output


def beautify_html(txt):
    txt = txt.split('\n')  # Now contains array of line
    txt = nocomments(txt)
    txt = nochr(txt)
    txt = nowrap(txt)
    txt = tabit(txt, "HTML")
    txt = colorit(txt, "HTML")   # HTML/TEXT
    return ''.join(txt)


def beautify_txt(txt):
    txt = txt.split('\n')  # Now contains array of line
    txt = nocomments(txt)
    txt = nochr(txt)
    txt = nowrap(txt)
    txt = tabit(txt, "TEXT")
    txt = colorit(txt, "TEXT")   # HTML/TEXT
    return '\n'.join(txt)


# Main Code #####
def main():
    filename = getparam(1)
    txt = open(filename)
    txt = txt.read()  # Now contains UTF strings
    txt = beautify_txt(txt)
    print txt

if __name__ == '__main__':
    main()
