clean:
	rm runpe.exe
	rm runpeasm.o
	rm hello.exe

hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe

runpeinc: runpeinc.asm
	 yasm -f win32 -g cv8 -m x86 runpeinc.asm -o runpeinc.o

runpe: runpeinc hello runpe.cpp
	i586-mingw32msvc-g++  -O1 runpeinc.o runpe.cpp -o runpe.exe -D_UNICODE -mwindows
	#strip runpe.exe
#	upx runpe.exe
