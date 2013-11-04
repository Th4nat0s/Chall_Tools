#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <winsock2.h>

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


typedef HINSTANCE (WINAPI * PLoadLibrary ) ( LPCTSTR lpLibFileName ); 
typedef LONG (WINAPI * PGetProcAddress)( HMODULE hModule,LPCSTR lpProcName );
typedef LPTCH (WINAPI *  PGetEnvironmentStringsA) (void);

int main(){
	char *content; 
	int size;
	LPVOID pFile;
	pFile = FileToMem("c:\\windows\\system32\\kernel32.dll");
//  pFile[295] = 0x50; // Change Load offset

///	asm ("int3");
  FILE * wFile;
  wFile = fopen ("c:\\mykernel.dll", "wb");
  fwrite (pFile, sizeof(char), esize , wFile);
  fclose (wFile);
PGetProcAddress xGetProcAddress;
PGetEnvironmentStringsA xGetEnvironmentStringsA;
	HINSTANCE Hkernel32  = LoadLibrary("c:\\mykernel.dll");

printf("kernel32 getprocadd\n");
   xGetProcAddress = PGetProcAddress(GetProcAddress(Hkernel32,"GetProcAddress"));
printf("mylib getprocadd\n");
xGetEnvironmentStringsA = PGetEnvironmentStringsA(xGetProcAddress(Hkernel32,"GetEnvironmentStringsA"));

printf("mylib envstring\n");
	xGetEnvironmentStringsA();
printf("kernel32 envstring\n");
	GetEnvironmentStringsA();

}
