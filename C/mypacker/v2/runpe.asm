align 16

%include "macro.asm"

section .data
PEBASE dd 0
%include "payload.inc"
boxtext db "Hello World",0
boxtitle db "Message",0

section .text
payload incbin  "payload.bin"

%include "bbcypher.asm"

GLOBAL _start

; ########## MAIN PROGRAM ##############
_start:
	; Reserve Memory for the PE image
	invoke _VirtualAlloc@16, NULL,dword [PELEN], MEM_COMMIT, PAGE_READWRITE
	mov	[PEBASE], eax ; Save memory location

	call _bbdecypher
	
	; Popup
	invoke _MessageBoxA@16, 0, boxtext, boxtitle, 0
	invoke _ExitProcess@4, NULL

	ret

