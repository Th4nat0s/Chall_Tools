#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <winsock2.h>
#include <stddef.h>
int esize;
LPVOID FileToMem(LPCSTR szFileName) { 
	HANDLE hFile;
	DWORD dwRead;
	DWORD dwSize;
	LPVOID pBuffer = NULL;
 
 	hFile = CreateFileA(szFileName, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, NULL, NULL);
 	if (hFile) {
 		dwSize = GetFileSize(hFile, NULL);
 		if (dwSize > 0) {
		  esize = dwSize;
 			pBuffer = VirtualAlloc(NULL, dwSize, MEM_COMMIT, PAGE_READWRITE);
 			if (pBuffer) {
 				SetFilePointer(hFile, NULL, NULL, FILE_BEGIN);
 				ReadFile(hFile, pBuffer, dwSize, &dwRead, NULL);
 			}
 		}
 		CloseHandle(hFile);
 	}
 	return pBuffer;
}


void replace_str( char * buff,int bsize, char *  what, char * to){
	int i,j,win;
	for(j = 0; j <= bsize ; ++j) {
		if (buff[j] == what[0]) {  // Find first letter
			win=0;
			for ( i = 0; i <= strlen(what)+1 ; i++) {
				if (buff[i+j] == what[i]) {  // Compare string 
				  win++;
	    	}
			}
  		if (win == strlen(what)+1) {  // FOUND
				printf("found at %d\n",j);
				for ( i = 0; i <= strlen(what) ; i++) {
				      buff[i+j] = to[i];  // replace string
						}
			}
		}
	}
}

typedef HINSTANCE (WINAPI * PLoadLibrary ) ( LPCTSTR lpLibFileName ); 
typedef LONG (WINAPI * PGetProcAddress)( HMODULE hModule,LPCSTR lpProcName );
typedef LPTCH (WINAPI *  PGetEnvironmentStringsA) (void);
typedef VOID (WINAPI * PSleep) ( DWORD dwMilliseconds);

int extern getfunction( int kernel, int library ) asm ("_getfunction");

int main(){
	char *content; 
	int size;
	LPVOID pFile;
	pFile = FileToMem("c:\\windows\\system32\\kernel32.dll");
	char * buffer = (char *)pFile;
	buffer[295] = 0x60; // Change Load offset
	char toto[]=  "GetProcAddress";
	char titi[] = "HelloMyFriends";

	char atoto[]=  "GetEnvironmentStringsA";
	char atiti[] = "ILoveBigRabbitsandDead";

	char btoto[]=  "Sleep";
	char btiti[] = "Lapin"; 
	
	char ktoto[]=  "KERNEL32";
	char ktiti[]=  "LAPINCON";
	replace_str(buffer,esize , toto, titi );
	replace_str(buffer,esize , ktoto, ktiti );
	replace_str(buffer,esize , atoto, atiti );
	replace_str(buffer,esize , btoto, btiti );

///	asm ("in$t3";
  FILE * wFile;
  wFile = fopen ("c:\\mykernel.dll", "wb");
  fwrite (buffer, sizeof(char), esize , wFile);
  fclose (wFile);
	PGetProcAddress xGetProcAddress;
	PGetEnvironmentStringsA xGetEnvironmentStringsA;
  PSleep xSleep;

	printf("Load tuned kernel32\n");
	HINSTANCE Hkernel32  = LoadLibrary("c:\\mykernel.dll");
	printf("new kernel at %X", (int) Hkernel32);
	
	printf("Find getprocadd\n");
  xGetProcAddress = (PGetProcAddress) getfunction((int)Hkernel32, (int)&titi );
	printf("GetProcAddress at %X\n",(int) xGetProcAddress);
//	GetLastError();


	printf("Find Sleep\n");
  xSleep = (PSleep) getfunction((int)Hkernel32, (int)&btiti );
	printf("Sleep at %X\n",(int) xSleep);
//	GetLastError();



	printf("find a lib with mylib getprocadd\n");
	xGetEnvironmentStringsA = (PGetEnvironmentStringsA) getfunction ((int)Hkernel32,(int)&atiti);

	printf("find a lib with mylib getprocadd\n");

printf("call mylib envstring\n");
	xGetEnvironmentStringsA();
printf("call kernel32 envstring\n");
	GetEnvironmentStringsA();


printf("call mylib sleep\n");
	xSleep(10000);
printf("call kernel32 sleep\n");
	Sleep(10000);
	printf("bye");


}
