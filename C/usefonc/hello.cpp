#include <windows.h>
#include <stdio.h>

char obf[] = "HAL";
int key = 1;

int unobf(int incr, char  mystring[]) {
  char i=0;
  do {
      mystring[i] =  mystring[i] + incr;
      i++; 
    } while (mystring[i] != 0);
}

int main(){
  printf( "Obfuscation Function at %p\n", int(unobf));
  printf( "Obfuscated string at  %p\n", int(&obf));
  printf( "Obfuscated Key at  %p\n", int(&key));
  unobf( 1, obf);
  printf( "The computer brand is %s\n", obf);
  return(0);
}
