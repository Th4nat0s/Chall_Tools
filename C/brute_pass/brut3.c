/*
brute.c

(c) Thanat0s.trollprod.org / 2013 

ascii de 32 a 126 = 
	Jusque 6 char 742.912.017.120  742 Milliards...
*/

// ************ LIB ***************
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <semaphore.h>

int extern mybrute () asm ("mybrute") ; // (unsigned char *);

#define True 1;
#define False 0;

// ************ Variables **********

int	g_pass_min ; // min char len
int g_thread , g_map;  
int g_char_max,pass_len,g_pass_len, g_char_min;
int g_break_on_win, g_print ;
char g_map_char[255];
int (*hash_fonc)( char * );

sem_t mutex;  // semaphore 
pthread_mutex_t lock; // lock

typedef struct {
	int	tid;
	int max_len;
	int char_max;
	int min_char;
	int str_min;
	int str_max;
} brute_mythread_struct;

// ************ CODE ***************

// TimeStamp print
void timeprint(void) {
	struct tm *current;
	time_t now;
	time(&now);
	current = localtime(&now);
	printf("%02d:%02d:%02d ", current->tm_hour, current->tm_min, current->tm_sec);
}

// Hexadecimal print
void hexprint( char buf[255],int x) {
	int i;
	for (i = 0; i < x; i++) {
    if (i > 0) printf(":");
		    printf("%02X", buf[i]);
				}
}


int bigerror( char *mystring) {
	printf("Error: %s\n",mystring);
	exit(1);
}

int print_pass( char *mystring) {
	//printf("%s\n",mystring);
	//fputs(mystring,stdout); 
	//fputs("\n",stdout); 
	puts(mystring);
	return(0);
}

// BruteForce loop from AAA to ZZZ
void * brute_force (void *args) {
  //int max_len,char_max, min_char,str_min, str_max;
	 char tmp_buff[255];
	int idx,max_len,char_max,str_max,min_char;
  
	brute_mythread_struct *actual_args = args;
	max_len = actual_args->max_len ; 
	char_max = actual_args->char_max;
	min_char = actual_args->min_char ;
  str_max = actual_args->str_max ;
	
	// remplis le buffer de AAA + Start Char
	for (idx = 0; idx < actual_args->max_len; ++idx) { 
  	tmp_buff[idx]= actual_args->min_char;
  }
  tmp_buff[actual_args->max_len-1]=actual_args->str_min;
	tmp_buff[actual_args->max_len]=0; // Create StringZ


	if (g_print ) {
		pthread_mutex_lock(&lock);
		timeprint();
		printf ("Len %d Thread %i start: '%.*s%c' to  '%.*s%c' \n",max_len,actual_args->tid , max_len-1, tmp_buff, actual_args->str_min,max_len-1, tmp_buff, str_max);  
		pthread_mutex_unlock(&lock);
 	}

	// When spare time....
	// The Big working Loop.. tant que le dernier char est <...
	while (tmp_buff[max_len-1] <= str_max ) {
	for (idx = min_char; idx <= char_max  ; idx++ )  { // loop on 1st Char
			if ((*hash_fonc)(tmp_buff)) { // Test candidat
					pthread_mutex_lock(&lock);
					timeprint();
					printf("! Found -->");
					hexprint(tmp_buff,max_len);
					printf ("<-->%s<--\n",tmp_buff);
					pthread_mutex_unlock(&lock);
					if (g_break_on_win)	exit(0);  // Break on WIN
			}	
		tmp_buff[0]++ ; // inc char
		}

	// apres 1char, Scan et inc/dec char autour
		for (idx = 0; idx < max_len-1; idx++)  { 
    	if (tmp_buff[idx] > char_max ) {  // inc char suivant
     		tmp_buff[idx] = min_char;
       		tmp_buff[idx+1]++;
      	}
	  }
	}
	// End Big working loop...

	if (g_print ) {
		pthread_mutex_lock(&lock);  // print byebye
		timeprint();
		printf ("Thread %d finished\n",actual_args->tid);
		pthread_mutex_unlock(&lock);
	}
	
	sem_post(&mutex);       /* up semaphore */
	// End Threaad
  pthread_exit(0);
}

// Main programm
int mainjob() {
  int i,slot,interval,reste,charlen; 
  int cand_min, cand_max;
  
  pthread_t mythreads[g_thread];
  sem_init(&mutex, 0,g_thread-1); 

  for (pass_len = g_pass_min; pass_len <= g_pass_len ; pass_len++ )  { 
    charlen = (g_char_max - g_char_min) + 1;
    if ( g_thread > charlen ) g_thread = charlen ;
	interval = charlen / g_thread;
	reste = charlen - ( interval * g_thread );

	slot = 0;

	// Launch loop
	for ( i=0; i < g_thread; ++i ) {
	  // job distribution	
	  cand_min = slot + g_char_min;
	  if (reste > 0) {
	    slot++;
				reste--;
			}
			slot = slot + interval - 1;
			cand_max = slot + g_char_min;
			slot++;
			
      brute_mythread_struct *args = malloc(sizeof (brute_mythread_struct));
      args->max_len = pass_len;
      args->char_max = g_char_max;
      args->min_char = g_char_min;
      args->str_min = cand_min;
      args->str_max = cand_max;
      args->tid = i;
			  
			// Start job & Free ram
			if (pthread_create(&mythreads[i], NULL, brute_force, args)) {
            free(args);
      } 

		// Wait for thread free
    sem_wait(&mutex);       /* down semaphore */ 

		}
	}

	// Wait before finish
  for (i = 0; i < g_thread; ++i ) {
		pthread_join (mythreads[i], NULL);
  }

	if ( g_print){
	timeprint();
	puts("All job done");
	}
	return 0;
}

int main( int argc, char *argv[] ){
	int idx;
	
	// Create mutex lock
	if (pthread_mutex_init(&lock, NULL) != 0) {
		printf("\n mutex init failed\n");
		return 1;
	}

	// Set default values
	g_thread =4 ; // Thread 
	g_pass_min =1 ; // Max char len
	g_pass_len =4 ; // Max char len
	g_char_min = 97; // min char commence au espace
  	g_char_max = 122; // Maximum tilda
 	g_break_on_win = True ; // true ;
	g_print = True; // Print Debug
	g_map = False; // Print Debug
	g_map_char[0]=0;

	// Set default Hash
	hash_fonc = &mybrute;

	// Parse cmd line args
	if	(argc >=1 ){
	  for (idx = 1 ; idx < argc; idx++){
        // print Help
		if (strcmp(argv[idx],"-h") ==0 ) {
	      printf("Brut3  - (c) Thanat0s - 2013\nUsage:\n\t-t [int] thread\n\t-M [int] max char\n\t-m [int] min char\n");
		  printf("\t-print only output pwd\n\t-q quiet mode\n\t-c [Aa0FC] Standard charset\n\t-cc [charset] only if '-c C' is selected\n");
		  printf("\t-nowin don't stop on find\n");
		  printf("Default %d Threads, %d-%d All printable\n",g_thread,g_pass_min,g_pass_len);
		  exit(0);
		} 
		// Select threads
		if (strcmp(argv[idx],"-t") ==0 ) {
		  idx++;
		  if (argc == idx) bigerror( "-t Missing value");
	      g_thread = atoi( argv[idx])	;
		  if (g_thread == 0) bigerror("Use -t num where threads >=1");
		}	
		if (strcmp(argv[idx],"-m") ==0 ){
		  idx++;
		  if (argc == idx) bigerror( "-m Missing value");
		  g_pass_min = atoi( argv[idx])	;
		  if (g_pass_min == 0) bigerror("Use -m where min lenght >=1");
		}	
		if (strcmp(argv[idx],"-M") ==0 ){
		  idx++;
		  if (argc == idx) bigerror( "-M Missing value");
		  g_pass_len = atoi( argv[idx])	;
		  if (g_pass_len == 0) bigerror("Use -M where max lenght >=1");
		}
		if (strcmp(argv[idx],"-q") ==0 ){
		  g_print = False;
		}
		if (strcmp(argv[idx],"-print") ==0 ){
		  char buffer[65535];
		  setvbuf(stdout, buffer, _IOFBF, sizeof(buffer));
		  hash_fonc = &print_pass;
		  g_break_on_win = False;
		  g_print = False;
		}
		if (strcmp(argv[idx],"-nowin") ==0 ){
		  g_break_on_win = False;
		}
		if (strcmp(argv[idx],"-c") ==0 ) {
		  idx++;
		  if (argc == idx) bigerror( "-C Missing value");
		  if (strcmp(argv[idx],"a")==0) { g_char_min = 97; g_char_max = 122; } else // a-z
		  if (strcmp(argv[idx],"A")==0) { g_char_min = 65; g_char_max = 90 ; } else // A-Z
		  if (strcmp(argv[idx],"0")==0) { g_char_min = 48; g_char_max = 57 ; } else // 0-9
		  if (strcmp(argv[idx],"F")==0) { g_char_min = 32; g_char_max = 126; } else // Full
		  if (strcmp(argv[idx],"C")==0) { g_map = True; } else { 
		  bigerror ("Unknown Charactere scheme"); // Custom
		  } 	
		 
		 //eelse {
		//  	bigerror ("Unknown Charactere scheme"); // Custom
		}

		// parse charlen
		if (strcmp(argv[idx],"-cc") ==0 ) {
		  idx++;
		  if (argc == idx) bigerror( "-cc Missing value") ;
		  strcpy(g_map_char,argv[idx]);
	  	}
	  }
	}

	// Variable post parse check
	if ( hash_fonc == &print_pass) g_thread = 4; // When to display one thread only
	if (g_pass_len < g_pass_min) bigerror("Min an Max len inconcistencies") ; 
	if (g_map_char[0] == 0 ) {
	 	puts("toto");
	 	 if ( g_map == 1 )	bigerror("custom charset not specified") ;
		}
	
	//hash_fonc = &mybrute;

	// print job
	printf("JOB Summary: Thread %d, Len %d-%d, Charset '%c' to '%c'\n",g_thread,g_pass_min,g_pass_len,g_char_min,g_char_max);
	
	// Start the JOB
	mainjob();
	
	// Cleanp
	pthread_mutex_destroy(&lock);
	return 0;
}
