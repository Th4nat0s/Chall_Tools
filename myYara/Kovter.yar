/*
    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as long as you use it under this license.

*/

import "pe"

rule Kovter {
     meta:
        description = "Kovter Malware"
        author = "Th4nat0s"
        reference = "http://www.cyphort.com/kovter-ad-fraud-trojan/"
        date = "2015/11/11"
	strings:
        $mz="MZ"
        $c_borland = "SOFTWARE\\Borland\\Delphi\\RTL"
        $c_communist = "Lenin_SHDocVw"
        $c_jsinject = "els=document.getElementsByTagName('object');"
        $c_indll   = "222.dll"
        $c_os1 ="Win 2000"
        $c_os2 ="Win Server 2003 R2"
        $c_os3 ="Win Server 2008 R2"
        $c_os4 ="Win Server 2012 R2"
        $c_os5 ="Win 10"
        $c_play = "try {jwplayer().play()} catch(e){}"
        $c_hou = "@ouh"

	condition:
        ($mz at 0) and all of ($c*)
}
