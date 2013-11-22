clean:
	rm *.obj 
	rm runpe.exe
	rm hello.exe

hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

helloinc: hello
	./obfpe.py hello.exe

runpe: helloinc runpe.res
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine ../../../../masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../../masm/user32.lib ../../../../masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null

runpe.res: runpe.rc
	i586-mingw32msvc-windres runpe.rc runpe.res -O resp

all: hello helloinc

