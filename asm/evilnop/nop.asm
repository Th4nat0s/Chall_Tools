
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
caption db "Evil Nop Test", 0
txt1 db "We will start the nop",0
txt2 db "Nop was done",0


; Code Section
section .code
GLOBAL _start
_start:

 ; Stealth version of MessageBox 
 invoke _MessageBoxA@16, 0, caption, txt1, 0
   nop
   nop
   nop
   nop
   %include "nop.inc"
   nop
   nop
   nop
   nop
 ; End of nop test
 invoke _MessageBoxA@16, 0, caption, txt2, 0
 ; Appelle la popup discretos
   invoke _ExitProcess@4, NULL

