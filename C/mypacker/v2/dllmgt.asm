; ###################################################
; trouve un offset de dll by hash, 
; return 0 si pas trouvé
 
.data
peb	dd	0
.code

align 16
_getdll:
	mov	 eax,[fs:30]
	mov	[peb],eax

  push ebp
	mov  ebp,esp

  mov  ebx, [peb]  				;  pointer sur PEB  fs:0x30
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
	rol ecx,4
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
 ret
