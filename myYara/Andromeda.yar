/*
    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as long as you use it under this license.

The detection work on the injected process usually (msiexec.exe)

*/

rule Andromeda {
     meta:
        description = "Andromeda Malware"
        author = "Th4nat0s"
        reference = "https://www.botconf.eu/wp-content/uploads/2015/12/OK-P07-Jose-Esparza-Travelling-to-the-far-side-of-Andromeda-2.pdf"
        date = "2016/03/14"
	strings:
        $c_v210 = "{\"id\":%lu,\"bid\":%lu,\"os\":%lu,\"la\":%lu,\"rg\":%lu,\"bb\":%lu"
        $c_v210b =  "{\"id\":%lu,\"tid\":%lu,\"err\":%lu,\"w32\":%lu}"
        $c_v209 = "id:%lu|bid:%lu|bv:%lu|sv:%lu|pa:%lu|la:%lu|ar:%lu"
        $c_v208 = "id:%lu|bid:%lu|bv:%lu|os:%lu|la:%lu|rg:%lu"
        $c_v209 = "id:%lu|bid:%lu|os:%lu|la:%lu|rg:%lu"

    condition:
        any of them
}
