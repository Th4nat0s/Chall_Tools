clean:
	rm nop*.obj 
	rm nop.inc

nop: nop.asm
	echo "db 0x90" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop.obj /verbose 2>/dev/null

nop2: nop.asm
	echo "db 0x66, 0x90" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop2.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop2.obj /verbose 2>/dev/null

nop3: nop.asm
	echo "db 0x0F, 0x1F, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop3.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop3.obj /verbose 2>/dev/null

nop4: nop.asm
	echo "db 0x0F, 0x1F, 0x40, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop4.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop4.obj /verbose 2>/dev/null

nop5: nop.asm
	echo "db 0x0F, 0x1F, 0x44, 0x00, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop5.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop5.obj /verbose 2>/dev/null

nop6: nop.asm
	echo "db 0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop6.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop6.obj /verbose 2>/dev/null

nop7: nop.asm
	echo "db 0x0F, 0x1F, 0x80, 0x00, 0x00, 0x00, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop7.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop7.obj /verbose 2>/dev/null

nop8: nop.asm
	echo "db 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop8.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop8.obj /verbose 2>/dev/null

nop9: nop.asm
	echo "db 0x66, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00" > nop.inc
	yasm -f win32 -m x86 nop.asm -o nop9.obj
	wine ../../../masm32/bin/polink /ENTRY:start /SUBSYSTEM:WINDOWS ../../../masm32/lib/user32.lib ../../../masm32/lib/kernel32.lib nop9.obj /verbose 2>/dev/null


all: nop nop2 nop3 nop4 nop5 nop6 nop7 nop8 nop9
