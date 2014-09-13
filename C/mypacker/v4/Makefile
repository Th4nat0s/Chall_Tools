clean:
	rm hello.exe ; true
	rm payload.inc ; true
	rm payload.bin ; true
	rm runpe.res ; true
	rm runpe.obj ; true
	rm hello.h ; true
	rm runpe.exe ; true
	rm packed.exe ; true

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
path = ../../../../
output = packed.exe
runpe: runpe.res hashsinc helloinc runpe.res 
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine $(path)masm/polink /ENTRY:start /SUBSYSTEM:CONSOLE $(path)masm/msvcrt.lib $(path)masm/user32.lib $(path)masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null
	sed 's/.text\x00/UPX0\x00\x00/' runpe.exe > temp
	sed 's/.data\x00/UPX1\x00\x00/' temp > $(output)
	rm runpe.exe
	rm temp

# Resources incones
runpe.res: runpe.rc
	i586-mingw32msvc-windres runpe.rc runpe.res -O res

all: hello helloinc runpe

pack: helloinc runpe

