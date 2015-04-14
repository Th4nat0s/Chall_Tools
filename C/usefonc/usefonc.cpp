#include <windows.h>
#include <stdio.h>


int extern callfunct(int outdata, int key, int offset) asm ("_callfunct") ; 

int main(int argc, char *argv[]){
  if (argc < 3) {
    printf ("Usage: \n%s monexe paramfile\n",argv[0]);
    return(1);
  }

  FILE *file;
  char *buffer;
  unsigned long fileLen;

  //Open file
  printf("Loading %s in memory\n",argv[1]);
  file = fopen(argv[1], "r+b");
  if (file) {
    //Get file length
    fseek(file, 0, SEEK_END);
    fileLen=ftell(file);
    fseek(file, 0, SEEK_SET);
    //Allocate memory
    buffer=(char *)malloc(fileLen+1);
    if(!buffer) {
      printf("Out of memory!\n");
      return EXIT_FAILURE;
    } else {
      //Read file contents into buffer
      fread(buffer, fileLen, 1, file);
      printf("load file ok\n");
  }} else {
    printf("Read %s error\n",argv[1]);
    return EXIT_FAILURE;
  }


  // Validate if it's a PE
  PIMAGE_DOS_HEADER IDH;  // Structure http://www.nirsoft.net/kernel_struct/vista/IMAGE_DOS_HEADER.html ^M
  PIMAGE_NT_HEADERS INH;
  PIMAGE_SECTION_HEADER ISH;
  IDH = PIMAGE_DOS_HEADER(buffer);
  if (IDH->e_magic == IMAGE_DOS_SIGNATURE) { // TEST MZ
    INH = PIMAGE_NT_HEADERS(DWORD(buffer) + IDH->e_lfanew);
    if (INH->Signature == IMAGE_NT_SIGNATURE) {   // TESTPE
    printf("PE32 Detected\n");
    } else {
    printf ("No PE Magic\n");
    return EXIT_FAILURE;
    } 
  } else {
    printf ("No MZ Magic\n");
    return EXIT_FAILURE;
  }

  // Allow required memory
  printf ("IMAGEBASE: 0x%08x\n", (int) INH->OptionalHeader.ImageBase) ;
  printf ("SIZEOFIMG: 0x%08x - %d Bytes\n", (int) INH->OptionalHeader.SizeOfImage, (int) INH->OptionalHeader.SizeOfImage);

  LPVOID pImageBase;
  pImageBase = VirtualAlloc( LPVOID(INH->OptionalHeader.ImageBase), INH->OptionalHeader.SizeOfImage, 0x3000, PAGE_EXECUTE_READWRITE);
  if (pImageBase) {
    printf ("Memory allocated");
    printf ("Current Process: 0x%08x\n", (int) pImageBase);
  } else {
    printf ("Could not allocate memory\n");
    printf ("Current Process: 0x%08x\n", (int) pImageBase);
    return EXIT_FAILURE;
  }
  
  // Map the PE
  int Count;
  WriteProcessMemory((void*)-1, pImageBase, buffer, INH->OptionalHeader.SizeOfHeaders, NULL);
  for (Count = 0; Count < INH->FileHeader.NumberOfSections; Count++) {
    ISH = PIMAGE_SECTION_HEADER(DWORD(buffer) + IDH->e_lfanew + 248 + (Count * 40));
    WriteProcessMemory((void*)-1, LPVOID(DWORD(pImageBase) + ISH->VirtualAddress), LPVOID(DWORD(buffer) + ISH->PointerToRawData), ISH->SizeOfRawData, NULL);
  }


  //Open command file
  char *command;
  printf("Loading command %s file\n",argv[2]);
  file = fopen(argv[2], "r+b");
  if (file) {
    //Get file length
    fseek(file, 0, SEEK_END);
    fileLen=ftell(file);
    fseek(file, 0, SEEK_SET);
    //Allocate memory
    command=(char *)malloc(fileLen+1);
    if(!command) {
      printf("Out of memory!\n");
      return EXIT_FAILURE;
    } else {
      //Read file contents into buffer
      fread(command, fileLen, 1, file);
    }
  }

  // Get line count in the command file...
  int i=0;
  int lines = 0;
  while (command[i] != 0) {
    if (command[i] == 0x0a) {
      lines++;
    } 
    i++;
  }
  lines++; // if lf missing on last line.
  printf ("Read %d command lines\n", lines);

  // Convert command file to integer array
  int paramcount = 3;
  int round = 0; 
  i=0;
  int j=1;
  int index;
  int index2;
  index = (int) command;
  int l = 0;

  char * temp;
  char * myhex;
  char * addr_array;
  char * addr_array_idx;
  int *ptr = (int*)malloc(paramcount * lines * sizeof *ptr);

  temp=(char *)malloc(512); // line parse
  myhex=(char *)malloc(8+1); // line parse
  while (command[i] != 0) {
    if (command[i] == 0x0a) {
      command[i] = 0;
      strcpy(temp,(const char*) index);
      if (temp[0] !=';') {
        printf ("line %d - %s\n", j , temp);
        round ++; 
        int k=0;

        index2 = (int) temp; 
        while (temp[k] != 0) {
          if (temp[k] == ',') {
            temp[k] = 0;
            strcpy(myhex,(const char*) index2 );
            ptr[l] = strtol( myhex, NULL, 16);
            l++;
            index2 = (int) temp + k + 1;

          }
         k++; 
        }
         strcpy(myhex,(const char*) index2 );
        ptr[l] =  strtol( myhex, NULL, 16);
            l++;

      }
      index =(int) command + i + 1;
      j++;
    }
    i++;
  }

  int cround=0;
  i = 0;
  round = l/3;
  while (cround < round ){
    int resoff ;
    resoff = callfunct ((int) ptr[i],(int) ptr[i+1],(int) ptr[i+2]);
    i=i+3;
    printf ("0x%08x:%s\n", (int) resoff, (int *) resoff);
    cround++; 
  }

  
  return(0);
}
