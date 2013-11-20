%define V_BBLEN EBP+0x0
%define V_ROWCNT EBP+0x4

_bbdecypher:
	push 	ebp
	mov	ebp,esp
	sub	ebp,16*4


	std  ; reverse stos/losd sens
	
	xor	edx,edx
	mov	eax,[PELEN]

	xor	ecx,ecx			; convert BBLEN to Dword
	add cl,[BBLEN]
	mov [V_BBLEN],ecx	

	idiv	ecx				; Calculate Row and Count
	dec eax
	mov	[V_ROWCNT],eax


	; Loop Géneral
.doallrowbbox:

	
	mov	ecx,[V_BBLEN]

	mov esi,payload
	add	esi,ecx 			; esi + V_BBLEN à la fin du BBkey

	mov	eax,[V_ROWCNT] ; Row x bblen
	mov edx,0
	mul	ecx						; x [V_BBLEN]

	mov	ebx,payload		; Debut de l'include
	add ebx,ecx				; + [V_BBLEN]	= Debut du PE bonneté
  add	ebx,eax				; Debut du PE bonneté + (Row x BBlen)
	
	mov	edi,[PEBASE] 	; Destination of PE
	add	edi,eax				; Destination du PE + (Row x BBLEN) 

	mov	eax,0

	call	_dorowbbox	; Decypher a row

	dec	dword [V_ROWCNT]
	jns	.doallrowbbox			; Jmp if 0 aussi

	cld
	
	add	ebp,16*4
	mov	esp,ebp
	pop	ebp
	
	ret

; Va Bonneter une rangée , use eax,ecx,edx,ebx
_dorowbbox:							
	mov		al,cl						; 
	xlatb									; Load byte à poser, src ebx+al
	mov	 	dl,al
	lodsb		 							; Deplacement a faire , read from bbkey
	mov	byte [edi+eax],dl ; pose byte + déplacement
	loop	_dorowbbox
	ret

