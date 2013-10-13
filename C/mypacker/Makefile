hello: hello.c
	i586-mingw32msvc-gcc hello.c -o hello.exe -lws2_32 
	strip hello.exe
	
runpe: hello
	i586-mingw32msvc-g++ runpe.cpp -o runpe.exe  -D_UNICODE -mwindows
	strip runpe.exe
	upx runpe.exe
