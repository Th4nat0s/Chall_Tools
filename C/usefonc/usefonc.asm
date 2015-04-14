section .data
   sauvegarde dd 0;
   myesp dd 0

section .text

GLOBAL _callfunct

_callfunct:
   ;int 3
   push  ebp
   mov   ebp,esp
   pusha
   mov   [myesp],esp

   mov   ebx,[ebp+0x08]  ; Second Parameter = Obf String
   mov   ecx,[ebp+0x0c]  ; Third Parameter = Key
   add   esp,256 ; keep space on stack


;---------------------------
   ; Remap function call as expected..
   push  ebx ;  Push Ascii String offset ( type pointer)
   
   mov   ecx,[ecx]
   push  ecx ;  push value of Key (type integer)
   
   call  [ebp+0x10] ; Call the fuction to decode

   ;int 3

   ; on the hello example the result in in EBX
   ; considerer ici que tous les registres sont détruit..
   mov   [sauvegarde],EBX
;-------------------------
   mov esp,[myesp]  ; Get back the stack on the good place
   popa
   pop   ebp
   mov   eax, [sauvegarde] ; Get back the string offset 
   ret
