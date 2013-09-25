section .text
GLOBAL mybrute 

mybrute:
	; Normalement il faut un appel 	
	;	qui sauve ebp et esp

	; Mais ici on touchera pas a la pile 
	; on s'en passe et on libere un registre

	;[esp] = retour addr
	;[esp+4]  = mystring
    
		mov   esi, dword [esp+4]    ; mystring
	 	mov   edi,ebx
		xor		eax,eax 	  ; pour nettoyer la partie haute d'eax
		lodsb							; On increment ESI, on met le 1er char dans AL
		mov		ebx, 0x539  ; Ebx sera le checksum, on y met le magicnumber

.locec6
		xor		ecx,ecx   ; xor 32, mov 8...
		mov	  cl,al 		; equivalent a movzx mais en moins de cycles
		mov		edx,ebx   ; [currentsum] est ebx
		shl		edx,5			; Multiplication
		add		ecx,edx	  ; Addition avec char 	
		add		ebx,ecx   ; Addition avec checsum 
		lodsb						; pointer+1, next char dans al
		test	al,al 	  ; est t'on a la fin de la stringZ ?
		jnz 	.locec6
		

		; Ici EAX est a O, pour le C 1 c'est true
		;cmp  	ebx, 0x02DE43DF ; TEST pour STRING ABC
		cmp  	ebx, 0xEF2E3558 ; TEST pour la string mystère
		mov ebx,edi
		je	.good
		ret
.good:
		inc eax
		ret
