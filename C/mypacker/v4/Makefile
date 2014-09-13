clean:
	rm hello.exe
	rm payload.inc
	rm payload.bin
	rm runpe.res
	rm runpe.obj
	rm hello.h
	rm runpe.exe

# The file embeded
hello: hello.c 
	i586-mingw32msvc-g++ hello.c -o hello.exe
	strip hello.exe

# Cypher the embeded file 
helloinc: hello
	./obfpe.py hello.exe

# DLL and Function hash generator
hashsinc: hashname.py
	./hashname.py

# Main compilation
runpe: runpe.res hashsinc helloinc runpe.res 
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine ../masm/polink /ENTRY:start /SUBSYSTEM:CONSOLE ../masm/msvcrt.lib ../masm/user32.lib ../masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null
	sed 's/.text\x00/UPX0\x00\x00/' runpe.exe > temp
	sed 's/.data\x00/UPX1\x00\x00/' temp > ch21.exe
	rm temp

runpe.res: runpe.rc
	i586-mingw32msvc-windres runpe.rc runpe.res -O res

all: hello helloinc runpe

