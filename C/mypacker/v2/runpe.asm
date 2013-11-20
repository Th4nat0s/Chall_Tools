align 16

%include "macro.asm"

section .data
PEBASE dd 0
%include "payload.inc"
boxtext db "Run",0
boxtitle db "Message",0

section .text
payload incbin  "payload.bin"

GLOBAL _start

_start:

%define	MEM_COMMIT 0x00001000
%define PAGE_READWRITE 0x04

	invoke _VirtualAlloc@16, NULL,dword [PELEN], MEM_COMMIT, PAGE_READWRITE
	mov	[PEBASE], eax
	
	mov	edi,[PEBASE]
	mov	esi,payload
	mov	ecx,[PELEN]
	rep movsb



	; Popup
	invoke _MessageBoxA@16, 0, boxtext, boxtitle, 0
	invoke _ExitProcess@4, NULL

	ret

