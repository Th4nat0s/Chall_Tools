
%define OBS ; Compiling with or without obfuscation
%define V_BBLEN EBP-((0x04*3)+RANDOMs)
%define V_ROWCNT EBP-((0x04*4)+RANDOMs)
%define V_BBDCIPH EBP-((0x04*5)+RANDOMs)

_bbdecypher:
	push 	ebp
	mov	ebp,esp

	std  ; reverse stos/losd sens
	

	%ifdef OBS
	push _dorowbbox + RANDOM16 ; Offset obfuscated du shif row
	%endif
	
	mov	eax,[PELEN]

	xor	ecx,ecx			; convert BBLEN to Dword
	add cl,[BBLEN]
	
	pop dword [V_BBDCIPH]
	mov [V_BBLEN],ecx	

	xor	edx,edx
	idiv	ecx				; Calculate Row and Count
	dec eax

	mov	dword [V_ROWCNT],eax


	; Loop Géneral
.doallrowbbox:
	mov	ecx,[V_BBLEN]

	mov esi,PAYLOAD
	add	esi,ecx 			; esi + V_BBLEN à la fin du BBkey
	dec	esi

	mov	eax,[V_ROWCNT] ; Row x bblen
	mov edx,0
	mul	ecx						; x [V_BBLEN]

	mov	edx,[V_BBDCIPH]
	mov	ebx,PAYLOAD		; Debut de l'include
	add ebx,ecx				; + [V_BBLEN]	= Debut du PE bonneté
  add	ebx,eax				; Debut du PE bonneté + (Row x BBlen)

	%ifdef OBS
	sub	edx,RANDOM16
	%endif

	mov	edi,[PEBASE] 	; Destination of PE
	add	edi,eax				; Destination du PE + (Row x BBLEN) 

	mov	eax,0
	

	%ifdef OBS
	call	edx				; Decypher a row
	%endif
	%ifndef OBS
	call _dorowbbox 
	%endif

	dec	dword [V_ROWCNT]
	jns	.doallrowbbox			; Jmp if 0 aussi

	cld
	
	mov	esp,ebp
	pop	ebp
	
	ret

; Va Bonneter une rangée , use eax,ecx,edx,ebx
_dorowbbox:							
	mov		al,cl
	dec   al
	xlatb									; Load byte à poser, src ebx+al
	mov	 	dl,al
	lodsb	 								; Deplacement a faire , read from bbkey
	mov	byte [edi+eax],dl ; pose byte + déplacement
	loop	_dorowbbox
	ret

