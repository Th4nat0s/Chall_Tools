
;  Macro & Constantes defintions
%define NULL 0

%macro invoke 2-*
  extern %1
  %rotate %0-1
  %rep  %0-1
    push    %1
    %rotate -1
  %endrep
  %rotate %0
  call  %1
%endmacro

%macro invokel 2-*
  %rotate %0-1
  %rep  %0-1
    push    %1
    %rotate -1
  %endrep
  %rotate %0
  call  %1
%endmacro

; Data section
section .data
txt1 db "Hello depuis des fonctions non Declarees",0
str_user32 db "user32.dll",0

FN_LOADLIBRARY dd 0
FN_MSGBOX dd 0 

%include "hashs.inc"

; Code Section
section .code
GLOBAL _start
_start:
	
 ;  Stealth version of MessageBox 
 ;  invoke _MessageBoxA@16, 0, txt1, txt1, 0
	
 ; Récupère la base addresse de Kernel32 
    invokel _getdll,HASH_KERNEL32.DLL
 ; Récuère l'offset de la fonctions LoadLibraryA
    invokel _getfunction, eax, HASH_LOADLIBRARYA
    mov [FN_LOADLIBRARY], EAX

 
 ; Charge user32.dll
    invokel [FN_LOADLIBRARY],str_user32
 
 
 ; Récupère l'addresse de base de user32.dll  
    invokel _getdll,HASH_USER32.DLL
 ; Récupère l'offset le la fonctions
    invokel _getfunction, eax, HASH_MESSAGEBOXA
    mov [FN_MSGBOX], EAX
  

  ; Appelle la popup discretos
    invokel [FN_MSGBOX], 0, txt1, txt1, 0
   
   
   invoke _ExitProcess@4, NULL

   %include "dllmgt.asm"
