clean:
	rm *.o
	rm runpe.exe
	rm hello.exe

hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

helloinc: hello
	./obfpe.py hello.exe

all: hello helloinc

