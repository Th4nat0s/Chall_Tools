ifdef outfile
 outfile = :
else
 outfile = runpe.exe
endif

ifdef infile
 infile = :
else
 infile = hello.exe
endif

clean:
	rm $(infile) ; /bin/true
	rm payload.inc ; /bin/true
	rm payload.bin ; /bin/true
	rm runpe.res ; /bin/true
	rm runpe.obj ; /bin/true
	rm hello.h ; /bin/true
	rm $(outfile) ; /bin/true
	rm packed.exe ; /bin/true

# The file embeded
hello: hello.c 
	i586-mingw32msvc-g++ hello.c -o hello.exe
	strip hello.exe

# Cypher the embeded file 
helloinc: 
	./obfpe.py $(infile)

# DLL and Function hash generator
hashsinc: hashname.py
	./hashname.py

# Main compilation
pathlink = ../../../../


runpe_cons: runpe.res hashsinc helloinc runpe.res 
	yasm runpe.asm -e > temp
	./PaulYmorphe.py temp > temp2
	yasm -f win32 -m x86 temp2 -o runpe.obj
	wine $(pathlink)masm/polink /ENTRY:start /SUBSYSTEM:CONSOLE $(pathlink)masm/msvcrt.lib $(pathlink)masm/user32.lib $(pathlink)masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null
	sed 's/.text\x00/UPX0\x00\x00/' $(outfile) > temp
	sed 's/.data\x00/UPX1\x00\x00/' temp > $(outfile)
	rm temp
	rm temp2

runpe: runpe.res hashsinc helloinc runpe.res 
	yasm -f win32 -m x86 runpe.asm -o runpe.obj
	wine $(pathlink)masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS $(pathlink)masm/user32.lib $(pathlink)masm/kernel32.lib runpe.res runpe.obj /verbose 2>/dev/null
	sed 's/.text\x00/UPX0\x00\x00/' $(outfile) > temp
	sed 's/.data\x00/UPX1\x00\x00/' temp > $(outfile)
	rm temp

# Resources incones
runpe.res: runpe.rc
	i586-mingw32msvc-windres runpe.rc runpe.res -O res

all: hello helloinc runpe.res runpe_cons

pack: helloinc runpe.res runpe
pack_cons: helloinc runpe.res runpe_cons

