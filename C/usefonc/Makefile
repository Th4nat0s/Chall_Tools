all: usefonc hello

clean:
	rm *.o hello.exe usefonc.exe

hello: hello.cpp
	i586-mingw32msvc-c++ -mconsole hello.cpp -o hello.exe

usefonc: usefonc.cpp
	i586-mingw32msvc-c++ -mwindows -O0 usefonc.cpp -c
	yasm -f win32 -g cv8 -m x86 usefonc.asm -o usefonc_asm.o
	i586-mingw32msvc-ld --image-base 0x20000000 --subsystem console -Bdynamic -o usefonc.exe usefonc.o usefonc_asm.o /usr/i586-mingw32msvc/lib/crt2.o -L/usr/lib/gcc/i586-mingw32msvc/4.2.1-sjlj -L/usr/i586-mingw32msvc/lib  -lstdc++ -lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt -lgdi32 -lcomdlg32 -luser32 -lkernel32 -ladvapi32 -lshell32 -lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt
