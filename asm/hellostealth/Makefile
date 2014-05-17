clean:
	rm nop.obj

# DLL and Function hash generator
hashsinc: hashname.py
	./hashname.py

nop: hashsinc
	yasm -f win32 -m x86 nop.asm -o nop.obj
	wine ../../../masm/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm/user32.lib ../../../masm/kernel32.lib nop.obj /verbose 2>/dev/null

all: nop

