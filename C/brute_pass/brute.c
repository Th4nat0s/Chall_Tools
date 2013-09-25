/*
brute.c
(c) Thanat0s.trollprod.org / 2013 

// jusque 6 char 742.912.017.120  742 Milliards...
*/

// ************ LIB ***************
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

int extern mybrute () asm ("mybrute");

// ************ CODE ***************

// TimeStamp print
void timeprint(void) {
	struct tm *current;
	time_t now;
		
	time(&now);
	current = localtime(&now);

	printf("%d:%d:%d ", current->tm_hour, current->tm_min, current->tm_sec);
}

// Hexadecimal print
void hexprint(unsigned char buf[255],int x) {
	int i;
	for (i = 0; i < x; i++) {
    if (i > 0) printf(":");
		    printf("%02X", buf[i]);
				}
}


typedef struct {
	int max_len;
	int char_max;
	int min_char;
	int str_min;
	int str_max;
} brute_mythread_struct;


// BruteForce loop from AAA to ZZZ
void * brute_force (void *args) {
  //int max_len,char_max, min_char,str_min, str_max;
	unsigned char tmp_buff[255];
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


 	// The Big working Loop.. tant que le dernier char est <...
	while (tmp_buff[max_len-1] <= str_max ) {

		for (idx = min_char; idx <= char_max; idx++ )  { // loop on 1st Char
		 //printf( "-->%s<--\n",tmp_buff);
			if ( mybrute(tmp_buff)) { // Test candidat
				  timeprint();
					printf("Got a Winner ---->");
					hexprint(tmp_buff,max_len);
					printf ("<->%s<---- WIN\n",tmp_buff);
					exit(0);  // Break on WIN
			}	
		tmp_buff[0]++ ; // inc char
		}

	// apres 1char, Scan et inc/dec char autour
		for (idx = 0; idx < max_len-1; idx++ )  { 
    	if (tmp_buff[idx] >= char_max ) {  // inc char suivant
     		tmp_buff[idx] = min_char;
       	tmp_buff[idx+1]++;
      }
		}
	}

	// End Thread
	return (0);
}


// Main programm
int main() {
int thread;  
int g_char_max,pass_len,g_pass_len, g_char_min;
int i,slot,interval,reste,charlen; 
	int cand_min, cand_max;
  
	unsigned char strbeg[255], strend[255];
	
	thread = 4; // Thread 
	g_pass_len = 5; // Max char len
	g_char_min =32; // min char commence au espace
  g_char_max = 126; // Maximum tilda


  pthread_t mythreads[thread];
  
	for (pass_len = 1; pass_len <= g_pass_len ; pass_len++ )  { 
		charlen = (g_char_max - g_char_min) + 1;

		if ( thread > charlen ) thread = charlen ;

		interval = charlen / thread;
		reste = charlen - ( interval * thread );

		for (i = 0; i <= pass_len; i++) {
			strbeg[i] = g_char_min;
			strend[i] = g_char_max;
		} 
		strbeg[i+1] = 0;
		strend[i+1] = 0;
  
		slot = 0;

		for ( i=0; i < thread; ++i ) {
			cand_min = slot + g_char_min;
			if (reste > 0) {
				slot++;
				reste--;
			}
			slot = slot + interval - 1;
			cand_max = slot + g_char_min;
			slot++;
			timeprint();
			
			printf ("Len %d Thread %i start: '%.*s%c' to  '%.*s%c' \n",pass_len, i+1, pass_len-1, strbeg, cand_min, pass_len-1, strend, cand_max);  
		
      brute_mythread_struct *args = malloc(sizeof (brute_mythread_struct));
      args->max_len = pass_len;
      args->char_max = g_char_max;
      args->min_char = g_char_min;
      args->str_min = cand_min;
      args->str_max = cand_max;
			  
			if (pthread_create(&mythreads[i], NULL, brute_force, args)) {
            free(args);
      }  

		}

		// Wait for sleep to terminate
 		for (i = 0; i < thread; ++i ) {
	 		pthread_join (mythreads[i], NULL);
 		}
	}
	timeprint();
	printf("Done, i didn't find it\n");
	return 0;
}
