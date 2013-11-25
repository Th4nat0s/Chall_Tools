clean:
	rm *.obj 
	rm runpe.exe
	rm hello.exe
	rm payload.inc
	rm payload.bin

# The file embeded
hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

# Cypher the embeded file 
helloinc: hello
	./obfpe.py hello.exe

# DLL and Function hash generator
hashsinc: hashname.py
	./hashname.py

nop:
	yasm -f win32 -m x86 nop.asm -o nop.obj
	wine ../../../../masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../../masm/user32.lib ../../../../masm/kernel32.lib nop.obj /verbose 2>/dev/null

# Main compilation
runpe: runpe.res hashsinc
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine ../../../../masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../../masm/user32.lib ../../../../masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null

runpe.res: runpe.rc
	i586-mingw32msvc-windres runpe.rc runpe.res -O resp

all: hello helloinc

