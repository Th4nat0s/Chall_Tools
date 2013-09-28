all: brut3

force: clean brut3

clean:
	rm brut3 *.o

brut3: brut3.c hash.o
	gcc -m32 -Wall -O3 -march=native -c brut3.c -lpthread 
	gcc hash.o brut3.o -lpthread -o brut3 -ggdb
	chmod +x brut3

hash.o: hash.asm
	yasm -f elf -m x86 hash.asm -o hash.o
	yasm -f bin -m x86 hash.asm -o hash.bin

install: brut3
	strip brut3
	mv brut3 /usr/local/bin
	chmod +x /usr/local/bin/brut3

uninstall: brut3
	rm /usr/local/bin/brut3
