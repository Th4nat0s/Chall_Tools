; Constant Definition 

%define NULL 0
%define MEM_COMMIT 0x00001000
%define PAGE_READWRITE 0x04

; Macro definition

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



