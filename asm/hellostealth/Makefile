clean:
	rm nop.obj

# DLL and Function hash generator
hashsinc: hashname.py
	./hashname.py

nop: hashsinc
	yasm -f win32 -m x86 nop.asm -o nop.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop.obj /verbose 2>/dev/null

all: nop

