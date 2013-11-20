clean:
	rm *.bin *.o
	rm runpe.exe
	rm hello.exe

hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

helloinc: hello
	./obfpe.py hello.exe

runpe: helloinc
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine ../../../../masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../../masm/user32.lib ../../../../masm/kernel32.lib runpe.obj /verbose 2>/dev/null

all: hello helloinc

