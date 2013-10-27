clean:
	rm *.o
	rm runpe.exe
	rm hello.exe
	rm ostring.inc

hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

obstrings: obstrings.py
	python obstrings.py > ostrings.inc

runpeinc: runpeinc.asm obstrings 
	 yasm -f win32 -g cv8 -m x86 runpeinc.asm -o runpeinc.o

runpe: runpeinc hello runpe.cpp
	i586-mingw32msvc-c++ -mwindows -O0  runpe.cpp  -c
	i586-mingw32msvc-ld --subsystem windows -Bdynamic -o runpe.exe /usr/i586-mingw32msvc/lib/crt2.o -L/usr/lib/gcc/i586-mingw32msvc/4.2.1-sjlj -L/usr/i586-mingw32msvc/lib runpeinc.o runpe.o -lstdc++ -lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt -lgdi32 -lcomdlg32 -luser32 -lkernel32 -ladvapi32 -lshell32 -lmingw32 -lgcc -lmoldname -lmingwex -lmsvcrt 
