.intel_syntax noprefix
.global _start
.section .text

_start:
    cld
    sub rsp, 0x28

    mov rbx, qword ptr gs:[0x60]
    mov rbx, qword ptr [rbx + 0x18]
    mov rbx, qword ptr [rbx + 0x20]
    mov rbx, qword ptr [rbx]
    mov rbx, qword ptr [rbx]
    mov rbx, qword ptr [rbx]
    mov rdi, qword ptr [rbx + 0x20]

    mov rcx, rdi
    mov edx, 0xec0e4e8e
    call resolve_hash
    mov r12, rax

    mov rcx, rdi
    mov edx, 0x7c0dfcaa
    call resolve_hash
    mov r13, rax

    mov rcx, rdi
    mov edx, 0x73e2d87e
    call resolve_hash
    mov r14, rax

    lea rcx, [rip + user32_dll]
    call r12
    mov r15, rax

    mov rcx, r15
    lea rdx, [rip + messagebox_a]
    call r13
    mov rbx, rax

    xor ecx, ecx
    lea rdx, [rip + text]
    lea r8, [rip + caption]
    xor r9d, r9d
    call rbx

    xor ecx, ecx
    call r14

resolve_hash:
    push rbx
    push rsi
    push rdi
    push r8
    push r9
    push r10
    push r11

    mov r8, rcx
    mov eax, dword ptr [r8 + 0x3c]
    add rax, r8
    mov eax, dword ptr [rax + 0x88]
    add rax, r8

    mov r9d, dword ptr [rax + 0x18]
    mov r10d, dword ptr [rax + 0x20]
    add r10, r8
    mov r11d, dword ptr [rax + 0x24]
    add r11, r8
    mov ebx, dword ptr [rax + 0x1c]
    add rbx, r8

find_name:
    test r9d, r9d
    jz not_found
    dec r9d
    mov esi, dword ptr [r10 + r9 * 4]
    add rsi, r8
    xor edi, edi

hash_loop:
    xor eax, eax
    lodsb
    test al, al
    jz hash_done
    ror edi, 13
    add edi, eax
    jmp hash_loop

hash_done:
    cmp edi, edx
    jne find_name
    movzx eax, word ptr [r11 + r9 * 2]
    mov eax, dword ptr [rbx + rax * 4]
    add rax, r8
    jmp done

not_found:
    xor eax, eax

done:
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rbx
    ret

user32_dll:
    .asciz "user32.dll"
messagebox_a:
    .asciz "MessageBoxA"
text:
    .asciz "Hello CIRCL"
caption:
    .asciz "Hello CIRCL"
