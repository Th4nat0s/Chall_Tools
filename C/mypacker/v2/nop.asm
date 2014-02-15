%include "macro.asm"
section .data
txt db "Hello"
section .code
GLOBAL _start
_start:
;	int 3
		 mov eax,0
	.gonop
		 nop
		 test eax,eax
		 je	.gonop
	 invoke _MessageBoxA@16, 0, txt, txt, 0
	 invoke _ExitProcess@4, NULL


