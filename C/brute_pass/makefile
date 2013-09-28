all: brut3

force: clean brut3

clean:
	rm brut3 *.o

brut3: brut3.c hash.o
	gcc -Wall -c brut3.c -lpthread 
	gcc hash.o brut3.o -lpthread -o brut3 -ggdb
	chmod +x brut3

hash.o: hash.asm
	yasm -f elf -m x86 hash.asm -o hash.o

