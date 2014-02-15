.code

align 16

; ###################################################
; trouve un offset de dll by hash, 
; return 0 si pas trouvé
;  In stack : Hash DLL name
; Out eax   : DLL Base address 

_getdll:

	mov	 eax,[fs:0x30]			; To BE REMOVED
	mov  dword	[PEB],eax

  push ebp
	mov  ebp,esp

  mov  ebx, [PEB]  				;  pointer sur PEB  fs:0x30
 	mov  ebx, [ebx+0x0C]    ;  pointeur sur  PEB->Ldr
	mov  ebx, [ebx+0x14]    ; flink premier module de la liste InMemoryOrder 
  mov  edx, [ebx+4]       ; blink... alias le point de sortie..  
  xor ecx,ecx
	xor	eax,eax
	jmp .startlist

.nextmod:
	cmp	ebx,edx
	je .tfini

.startlist:
	mov  esi, [ebx+0x28]    ;  pointeur sur la liste (unicode)

.readchar:
  lodsw			; lis un Word
  test al,al ; Fin de la string ?
  jz .stopreadchar
  
	cmp al,0x60  ; Si misuscule convert to Majuscule, 
	jbe .stoschar
	sub al,0x20 ; pass en majuscule
.stoschar
	xor	cl,al  ; Hash du pauvre, rolxor
	rol ecx,HASH_SFT
  jmp .readchar

.stopreadchar:
	cmp	 ecx,[ebp+0x8] ; Parametre 1, Hash DLL Name
	je .tfinifound

	mov ecx,0		; Reset the hash
	mov ebx, [ebx]         ; choppe le module suivant
	mov esi, [ebx+0x4]    ; module base address

	jmp	.nextmod

.tfinifound
	mov eax, [ebx+0x10]    ; module base address
	jmp	.tgohome

.tfini:
	mov	eax,0 		; pas trouvé l'offset return 0

.tgohome:

mov esp,ebp
 pop ebp
 retn 4



; ###################################################
; trouve un offset de fonction by hash 
; return 0 si pas trouvé
;  In stack : Hash Fonction
;  In stack : Offset DLL name
; Out eax   : Fonction Base address 

; trouve une fonction dans kernel32.dll
_getfunction:
   
	 push ebp
    mov  ebp,esp
  sub   eax,eax
  
  mov   eax,[ebp+0x8]
  mov   ebx, eax
  mov   edx,[eax+60] ; PE base loCATION
  add   eax, edx
  mov   edx,[eax] ; PE base dans EDX
  add   eax, 0x78
  mov   edx,[eax] ; Export Table offset
  add   ebx,edx  ;  edx = iat export table

  mov [ExpTable],ebx

  mov edx,[ebp+0xC]

  ExpTable   equ ebp-0x8

    mov esi, [ExpTable]

    mov esi, [esi+0x20] ;RVA 
    add esi, [ebp+0x8]  ;VA 
    xor ebx,ebx
    cld

    myloop:
          inc ebx
          lodsd
          add eax , [ebp+0x8]   ;eax sur les string des fonctions
          push esi       ; save pour la prochane loop
          mov esi,eax
          mov edi,edx
          cld
        ;  push ecx
				xor ecx,ecx

.readcharf:
  	lodsb     ; lis un Word
	  test al,al ; Fin de la string ?
		jz .stopreadcharf

		cmp al,0x60  ; Si misuscule convert to Majuscule, 
		jbe .stoscharf
		sub al,0x20 ; pass en majuscule
.stoscharf
	  xor cl,al  ; Hash du pauvre, rolxor
	  rol ecx,HASH_SFT
	  jmp .readcharf

.stopreadcharf

          pop esi
          
					cmp	ecx,[ebp+0xc] ; Hash Match ??
					
					jne myloop

          dec ebx
          mov eax,[ExpTable]
          mov eax,[eax+0x24]       ;RVA  EOT
          add eax,[ebp+0x8]     ;VA  EOT
          movzx eax , word [ebx*2+eax]  ;eax offset de la fonction
          mov ebx,[ExpTable]
          mov ebx,[ebx+0x1C]       ;RVA  EAT
          add ebx,[ebp+0x8]     ;VA  EAT
          mov ebx,[eax*4+ebx]
          add ebx,[ebp+0x8]
          mov eax,ebx

        mov esp,ebp
        pop ebp
        retn 8

_K32func:
	invokel _getdll,HASH_KERNEL32.DLL
  invokel _getfunction, eax, HASH_READPROCESSMEMORY
	ret

