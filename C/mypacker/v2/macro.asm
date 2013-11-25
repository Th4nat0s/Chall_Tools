; Constant Definition 

%define FALSE 0
%define CREATE_SUSPENDED 0x4
%define NULL 0
%define MEM_COMMIT 0x00001000
%define PAGE_READWRITE 0x04
%define PAGE_EXECUTE_READWRITE 0x40

; CPU Context
%define CONTEXT_FULL 0x10007
%define CTX__LEN 0x2CB
%define CTX__EAX 0xB0
%define CTX__EBX 0xA4
%define CTX__ECX 0xAC

; Process Information Structure
%define PROCESS_INFORMATION__hProcess 0
%define PROCESS_INFORMATION__hThread 4
%define	PROCESS_INFORMATION__dwProcessId 8
%define PROCESS_INFORMATION__dwThreadId 0xC

; Pe Optionnal Header structure
%define IMAGE_OPTIONAL_HEADER__LEN 0x60
%define IMAGE_OPTIONAL_HEADER__Magic 0
%define IMAGE_OPTIONAL_HEADER__ImageBase 0x1C
%define IMAGE_OPTIONAL_HEADER__AddressOfEntryPoint 0x10
%define IMAGE_OPTIONAL_HEADER__SizeOfImage 0x38
%define IMAGE_OPTIONAL_HEADER__SizeOfHeaders 0x3C

; PEB
%define PEB__ImageBaseAdress 0x8

; Pe IMAGE_DATA_DIRECTORY structure
%define IMAGE_DATA_DIRECTORY__LEN  0x70

; Structure IMAGE_SECTION_HEADER
%define IMAGE_SECTION_HEADER__LEN 0x28
%define IMAGE_SECTION_HEADER__Name 0x0
%define IMAGE_SECTION_HEADER__VirtualSize 0x8
%define IMAGE_SECTION_HEADER__VirtualAddress 0xC
%define IMAGE_SECTION_HEADER__SizeOfRawData 0x10
%define IMAGE_SECTION_HEADER__PointerToRawData 0x14

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



