all: brute

force: clean brute

clean:
	rm brute *.o

brute: brute.c hash.o
	gcc -Wall -c brute.c -lpthread 
	gcc hash.o brute.o -lpthread -o brute -ggdb
	chmod +x brute

hash.o: hash.asm
	yasm -f elf -m x86 hash.asm -o hash.o

