/*
    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as long as you use it under this license.

*/

rule Meterpreter {
     meta:
        description = "Rapid 7 Meterpreter RAT"
        author = "Th4nat0s"
        reference = "https://dev.metasploit.com/documents/meterpreter.pdf"
        date = "2016/03/14"
	strings:
        $s1 = "core_migrate"
        $s2 = "core_loadlib"
        $s3 = "packet_get_tlv_meta"
        $s4 = "packet_get_tlv_string"
        $s5 = "command_register"
        $s6 = "channel_find_by_id"
        $s7 = "POST"

    condition:
        all of them
}
