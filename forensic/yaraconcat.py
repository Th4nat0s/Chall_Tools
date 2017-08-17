#!/usr/bin/env python3
# coding=utf-8
import sys
import glob
import re


# Functions
def getparam(count):
    """Retrieve the parameters appended """
    if len(sys.argv) != count + 1:
        print('Concatenate a bunch of yarafiles and Warn on duplicate YaraRules')
        print('To Use: %s pathofyarafiles' % sys.argv[0])
        sys.exit(1)
    else:
        return sys.argv[1]


def parse(text):
    '''Convert a yara concatenation to dict of yara,
    takes care of duplicate rules name, keep order between rules

    Args:
        text(list): Text Array of concatened yara rules
    Returns:
        dict: Return dict of list of yara rules.
    '''
    idx = 0  # Index of rule
    ridx = 0  # Count of "{"
    pen, first = False, False
    rule = []
    rules = {}
    name = ""
    rules_names = {}
    comment = False
    regex = re.compile(r'rule\s+(\S+)', re.I)
    for line in text:
        line = line.strip('\n')

        if line.startswith('rule ') and not pen:
            name = regex.match(line).group(1)
            if rules_names.get(name):
                print ("/* Warning duplicate of %s */" % name)
            rules_names[name] = True  # Save to find duplicate
            name = ("%05d__%s" % (idx, name))  # Index name
            first, pen = True, True

        unquoted_line = re.sub(r'".*"', '""', line)
        unquoted_line = unquoted_line.replace("\\{",'')
        unquoted_line = re.sub(r'\/\*.*\*\/', '', unquoted_line).split("//")[0]

        print (idx, pen, "c", comment, line,"|", unquoted_line)
        if comment and "*/" in unquoted_line:
            comment = False
        if "/*" in unquoted_line:
            comment = True

        if pen and not comment:
            rule.append(line)
            ridx = ridx + unquoted_line.count('{')  # count {
            if "}" in unquoted_line:
                ridx = ridx - unquoted_line.count('}')  # count }
                if ridx == 0:
                    idx +=1
                    rules[name] = rule  # Store it with index
                    rule = []
        if ridx == 0 and not first:
            pen = False
        first = False

    print("/* %d Rules Processed */" % idx)
    return rules


def getimport(text):
    '''Retrieve import used by all Yara files'''
    regex = re.compile(r'import\s+\"(\S+)\"', re.I)
    import_f = {}
    for line in text:
        import_l = regex.match(line)
        if import_l:
            import_f[import_l.group(1)] = True
    return import_f


# Main Code #####
def main():
    param = getparam(1)
    yarafiles = glob.glob("%s/*.yar" % param)
    all_line = []

    print("/* %d Files Processed */" % len(yarafiles))
    for yarafile in yarafiles:
        curr_file = open(yarafile)
        lines = [i for i in curr_file.readlines()]
        curr_file.close
        all_line = all_line + lines

    # cr lf cleanup
    yar_rules = parse(all_line)

    print ("")
    # Print Import
    for imp in getimport(all_line):
        print ('import "%s"' % imp)
    print ("")
    for name in sorted(yar_rules):
        print ("\n".join(yar_rules[name]))
        print ("")


if __name__ == '__main__':
    main()
