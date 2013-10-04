/* Compile with:
   gcc -lz -lpthread -O3 -o bst  bst.c 
*/

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <errno.h>
#include <dirent.h>
#include <getopt.h>
#include <limits.h>
#include <libgen.h>
#include <zlib.h>
#include <time.h>
#include <pthread.h>
#include <regex.h>
#include <sys/stat.h>
#include <locale.h>

#define FIXED_STRING (1<<31)

#define PREFIX "ArcSight_Metadata_"
#define PREFIX_LEN 18
#define MD_BUFF_LEN 1024
#define MD_FSTLINE "ChunkId BeginOffset Length StartET EndET ReceiptTime ReceiverId EventCount ChunkVersion SourceType Flags"
#define MD_LINE_LEN 512
#define MD_FSTLINE_LEN 104

#define TIME_FMT "%F %T"
static char* sig = "\x74\x64\x63\x61\x2d\x2d\x4D\x4B";

#define ASIZE 256


typedef unsigned char uchar;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned long long ullong;
typedef struct _arg_t{
  char** path;
  ullong start;
  ullong end;
  FILE* out;
  pthread_mutex_t out_mutex;
  int cflags;
  char* pattern;
  uint pattern_len;
  int* pattern_bmGs;
  int pattern_bmBc[ASIZE];
  char* field;
  uint field_len;
  int* field_bmGs;
  int field_bmBc[ASIZE];
 
} arg_t;

#define MD_PARSE_NB 4
typedef struct _mdata_t{
  ulong BeginOffset; 
  ulong Length;
  ullong StartET;
  ullong EndET;
} mdata_t;

typedef struct _context_t{
  arg_t* arg;
  gzFile md_gzp; 
  pthread_mutex_t* md_mutex;
  FILE* d_fp;
  pthread_mutex_t* d_mutex;
  regex_t re;
} context_t;

typedef struct _mystr_t{
  char* s;
  uint len;
  uint occup;
} mystr_t;


void preBmBc(char *x, int m, int bmBc[]) {
  int i;
 
  for (i = 0; i < ASIZE; ++i)
    bmBc[i] = m;
  for (i = 0; i < m - 1; ++i)
    bmBc[x[i]] = m - i - 1;
}
 
 
void suffixes(char *x, int m, int *suff) {
  int f, g, i;
 
  suff[m - 1] = m;
  g = m - 1;
  for (i = m - 2; i >= 0; --i) {
    if (i > g && suff[i + m - 1 - f] < i - g)
      suff[i] = suff[i + m - 1 - f];
    else {
      if (i < g)
	g = i;
      f = i;
      while (g >= 0 && x[g] == x[g + m - 1 - f])
	--g;
      suff[i] = f - g;
    }
  }
}
 
void preBmGs(char *x, int m, int bmGs[]) {
  int i, j, suff[m];
 
  suffixes(x, m, suff);
 
  for (i = 0; i < m; ++i)
    bmGs[i] = m;
  j = 0;
  for (i = m - 1; i >= 0; --i)
    if (suff[i] == i + 1)
      for (; j < m - 1 - i; ++j)
	if (bmGs[j] == m)
	  bmGs[j] = m - 1 - i;
  for (i = 0; i <= m - 2; ++i)
    bmGs[m - 1 - suff[i]] = m - 1 - i;
}
 

int max (int a, int b){
  if (a > b)
    return a;
  return b;
}
 
char* BM(char *x, int m, char *y, int n, int* bmGs, int* bmBc) {
  int i, j; 
  j = 0;
  while (j <= n - m) {
    for (i = m - 1; i >= 0 && x[i] == y[i + j]; --i);
    if (i < 0) {
      return y + j;
      j += bmGs[0];
    }
    else
      j += max(bmGs[i], bmBc[y[i + j]] - m + 1 + i);
  }
  return NULL;
}

mystr_t*
mystr_build (uint len){
  mystr_t* mys = (mystr_t*)malloc(sizeof(mystr_t));
  mys->len = len;
  mys->s = (char*)malloc((mys->len) * sizeof(char));
  mys->occup = 0;
  mys->s[mys->occup] = 0;
  return mys;
}

void
mystr_realloc (mystr_t* mys, uint len){
  if (len < mys->len)
    return;
  mys->len = 2 * len;
  mys->s = (char*)realloc(mys->s, (mys->len) * sizeof(char));
}

void
mystr_free (mystr_t* mys){
  free(mys->s);
  free(mys);
}

enum{
  QUIET,
  NORMAL,
  VERBOSE,
  VERY_VERBOSE,  
};

uint THREAD_NB = 16;
uint VERBOSE_LEVEL = NORMAL;
char* DEFAULT_PATH = "./";
char* DEFAULT_PATTERN = NULL;

int
get_mdata (mdata_t* mdata, gzFile gzp, pthread_mutex_t* mutex){
  char buff[MD_LINE_LEN];
  pthread_mutex_lock (mutex);
  gzgets (gzp, buff, MD_LINE_LEN);
  pthread_mutex_unlock (mutex);
  int parsed = sscanf (buff, "%*u,%lu,%lu,%llu,%llu,%*s",
		       &mdata->BeginOffset,
		       &mdata->Length,
		       &mdata->StartET,
		       &mdata->EndET);
  return parsed == 4;
}

time_t start = 0, end;
ulong evt = 0;
ullong OUT_COUNT = 0;

void
print_out (char* s, context_t* context, ullong etime){
  int len = 0;
  if (s[0] == 0)
    return;
  arg_t* arg = context->arg;
  if (VERBOSE_LEVEL > NORMAL){
    pthread_mutex_lock (&arg->out_mutex);
    ++evt;
    if (evt > 10000){
      time(&end);
      double d = difftime (end, start);
      if (d > 5){
	fprintf (stderr, "%7.0f E/s\r", evt / d);
	fflush (stderr);
	evt = 0;
	time (&start);
      }
    }
    pthread_mutex_unlock (&arg->out_mutex);
  }
  
  if ((arg->cflags & FIXED_STRING) != 0){
    len = strlen (s);
    void* ret = BM (arg->pattern, arg->pattern_len, s, len, arg->pattern_bmGs, arg->pattern_bmBc);
    if (ret == NULL)
      return;
  }
  else if (regexec(&context->re, s, 0, NULL, 0) != 0)
    return;
  if (arg->out == NULL){
    pthread_mutex_lock (&arg->out_mutex);
    ++OUT_COUNT;
    pthread_mutex_unlock (&arg->out_mutex);
    return;
  } 
  time_t _time = etime/1000;
  char stime [21];
  if (arg->field != NULL){
    if (strncmp (s, "CEF", 3) != 0){
      pthread_mutex_lock (&arg->out_mutex);
      fputs (s, arg->out);
      fputc('\n', arg->out);
      pthread_mutex_unlock (&arg->out_mutex);
      return;
    }
    if (len == 0)
      len = strlen (s);
    pthread_mutex_lock (&arg->out_mutex);
    char* found = BM (arg->field, arg->field_len, s, len, arg->field_bmGs, arg->field_bmBc);
    pthread_mutex_unlock (&arg->out_mutex);
    if (found == NULL)
      return;
    found += arg->field_len;
    char* end = found;
    while (*end != 0 && (*end != '=' || *(end - 1) == '\\'))
      ++end;
    pthread_mutex_lock (&arg->out_mutex);
    if (*end == 0){
      while (*found != 0){
	if (*found != '\\' || *(found + 1) != '=')
	  fputc(*found, arg->out);
	++found;
      }
      fputc('\n', arg->out);
    }
    else{
      while (*end != ' ')
	--end;
      while (found < end){
	if (*found != '\\' || *(found + 1) != '=')
	  fputc(*found, arg->out);
	++found;
      }
      fputc('\n', arg->out);
    }
    pthread_mutex_unlock (&arg->out_mutex);
  }
  else{
    strftime(stime, sizeof(stime), TIME_FMT, gmtime(&_time));
    pthread_mutex_lock (&arg->out_mutex);
    fprintf (arg->out, "[%s] %s\n", stime, s);
    pthread_mutex_unlock (&arg->out_mutex);
  }
}

int 
extract_evt (int length, context_t* context, mystr_t* in, mystr_t* out){
  z_stream strm = {
    .zalloc = Z_NULL,
    .zfree = Z_NULL,
    .opaque = Z_NULL,
    .avail_in = 0,
    .next_in = Z_NULL,
  };
  int ret = inflateInit2(&strm, 16+MAX_WBITS);
  if (ret != Z_OK)
    return ret;
  strm.avail_in = length;
  strm.next_in = in->s;
  out->occup = 0;
  while (1) {
    strm.avail_out = out->len - out->occup;
    strm.next_out = out->s + out->occup;
    ret = inflate(&strm, Z_NO_FLUSH);
    if (strm.avail_out == 0){
      out->occup += out->len;
      mystr_realloc (out, 2 * out->len);
    }
    else{
      out->occup += out->len - strm.avail_out;
      break;
    }
  };
  int offset = 0;
  while (offset < out->occup){
    uchar* p = out->s + offset;
    ullong _time;
    uchar* p_time = (uchar*)&_time;
    int i;
    for (i = 0; i < 8; ++i)
      p_time[i] = p[7 - i];
    p += 8;
    uint evtlen;
    uchar* pevtlen =  (uchar*)&evtlen;
    for (i = 0; i < 4; ++i)
      pevtlen[i] = p[3 - i];
    p = out->s + offset + 0x20;
    if ((context->arg->start == 0 || context->arg->start <= _time)
	&& (context->arg->end == 0 || context->arg->end >= _time))
      print_out (p, context, _time);
    offset += evtlen + 0x20;
  } 
  inflateEnd(&strm);
  return Z_OK;
}


#define IN_INIT_SIZE 0x1000
#define OUT_INIT_SIZE 0x1000

void*
process_data(void* _context){
  context_t* context = (context_t*)_context;
  mystr_t* in = mystr_build (IN_INIT_SIZE);
  mystr_t* out = mystr_build (OUT_INIT_SIZE);
  
  mdata_t mdata;
  int cpt = 0;
  int ret;
  do {
    ret = get_mdata (&mdata, context->md_gzp, context->md_mutex);
    if ((context->arg->start != 0 && context->arg->start > mdata.EndET)
	|| (context->arg->end != 0 && context->arg->end < mdata.StartET))
      continue;
    mystr_realloc (in, mdata.Length);
    

    pthread_mutex_lock (context->d_mutex);
    fseek (context->d_fp, mdata.BeginOffset + 0x100, SEEK_SET);
    int len = fread(in->s, sizeof(char), mdata.Length, context->d_fp);
    pthread_mutex_unlock (context->d_mutex);
    
    int err = extract_evt (len, context, in, out);
  } while (ret != 0);
  mystr_free (in);
  mystr_free (out);
  return NULL;
}

void 
do_search(char* path, arg_t* arg){
  if (VERBOSE_LEVEL > NORMAL)
    printf ("processing: %s\n", path);
  gzFile gzp = gzopen (path, "rb");
  if (gzp == NULL){
    fprintf (stderr, "Cannot open '%s': %s\n", path, strerror (errno));
    gzclose (gzp);
    return;
  }
  char buff[MD_LINE_LEN];
  gzgets (gzp, buff, MD_LINE_LEN);
  if (strncmp(MD_FSTLINE, buff, MD_FSTLINE_LEN) != 0){
    printf ("error: %s unsupported header\n", path);
    gzclose (gzp);
    return;
  }
  
  pthread_mutex_t md_mutex;
  pthread_mutex_init(&md_mutex, NULL);

  char d_fpath[strlen(path)];
  d_fpath[0] = 0;
  strcpy (d_fpath, path);
  *basename(d_fpath) = 0;
    
  char* tok = strtok (basename(path),"_");
  strcat (d_fpath, tok);
  strcat (d_fpath, "_Data_");
  tok = strtok (NULL,"_");
  tok = strtok (NULL,"_");
  strcat (d_fpath, tok);
  tok = strtok (NULL,"_.");
  strcat (d_fpath, "_0");
  strcat (d_fpath, tok);
  strcat (d_fpath, ".dat");

  FILE* d_fp = fopen (d_fpath, "rb");
  if (d_fp == NULL){
    fprintf (stderr, "Cannot open '%s': %s\n", d_fpath, strerror (errno));
    return;
  }

  pthread_mutex_t d_mutex;
  pthread_mutex_init(&d_mutex, NULL);

  pthread_t thread[THREAD_NB];
  context_t context[THREAD_NB];
  size_t t;
  for (t = 0; t < THREAD_NB; ++t){
    context[t].arg = arg;
    context[t].md_gzp = gzp;
    context[t].md_mutex = &md_mutex;
    context[t].d_fp = d_fp;
    context[t].d_mutex = &d_mutex;
    if ((arg->cflags & FIXED_STRING) == 0){
      int ret = regcomp(&context[t].re, arg->pattern, arg->cflags); 
      if (ret != 0) {
	fprintf(stderr, "Bad regular expression\n");
	exit (1);
      } 
    }
  }
  for (t = 0; t < THREAD_NB; ++t)
    pthread_create (&thread[t], NULL, process_data, &context[t]);
  for (t = 0; t < THREAD_NB; ++t)
    pthread_join (thread[t], NULL);
  if ((arg->cflags & FIXED_STRING) == 0){
    for (t = 0; t < THREAD_NB; ++t)
      regfree (&context[t].re);
  }
  
  gzclose (gzp);
  fclose (d_fp);
}


void
_rsearch_setpath(char** path, uint* path_max, uint path_len, char* d_name){
  uint name_len = strlen (d_name);
  uint next_path_len = path_len +  name_len + 1;      
  (*path)[path_len] = '/';
  (*path)[path_len + 1] = 0;
  if (next_path_len> *path_max){
    *path_max = 2 * next_path_len;
    *path = realloc (*path, *path_max * sizeof(char));
  }
  strncat (*path, d_name, name_len);
}

void
_rsearch (char** path, uint* path_max, arg_t* arg)
{
  DIR *d = opendir (*path);
  if (d == NULL){
    fprintf (stderr, "Cannot open '%s': %s\n", *path, strerror (errno));
    return;
  }
  uint path_len = strlen (*path);
  while (1) {
    struct dirent* entry = readdir (d);
    if (entry == NULL) 
      break;
    switch (entry->d_type){
    case DT_DIR:
      if (entry->d_name[0] != '.'){
	_rsearch_setpath (path, path_max, path_len, entry->d_name);
	_rsearch (path, path_max, arg);
      }
      break;
    case DT_REG:
      if (strncmp(entry->d_name, PREFIX, PREFIX_LEN) == 0){
	_rsearch_setpath (path, path_max, path_len, entry->d_name);
	do_search(*path, arg);
      }
      break;
    }
  }
  closedir (d);
}  

void
rsearch(const char* path, arg_t* arg){
  uint path_max = 2 * strlen(path);
  char* _path = (char*)malloc (path_max * sizeof (char));
  strcpy (_path, path);
  _rsearch (&_path, &path_max, arg);
  free (_path);
}

void
print_usage (char* pname){
  printf("Usage: %s [OPTIONS] [PATTERN] [FILE ...]\n", basename(pname));
  printf("%s (aka blindshaft) searches for PATTERN in each FILE.\n", basename(pname));
  printf("\n");
  printf("PATTERN is a posix regular expression, default ouput all events.\n");
  printf("FILE is either a MetaData file or a directory. The latter recursively searches MetaData files in the directory. Default recursively search MetaData files in current directory; ie in \"./\".\n");
  printf("\n");
  printf("OPTIONS\n");
  printf("-E, --extended-regexp              PATTERN is an extended regular expression.\n");
  printf("-F, --fixed-string                 PATTERN is a a fixed string. This is the default.");
  printf("-G, --basic-regexp                 PATTERN is a basic regular expression\n");
  printf("-i, --ignore-case                  Ignore case distinctions.\n");
  printf("-f, --field FIELD                  Only output field FIELD.");
  printf("-s, --start \"YYYY-MM-DD HH:MM:SS\"  Set lower bound on the searched end time.\n");
  printf("-e, --end \"YYYY-MM-DD HH:MM:SS\"    Set greater bound on the searched end time.\n");
  printf("-t, --thread NBTHREAD              Set the number of threads. Default value is 16.\n");
  printf("-h, --help                         Print this message.\n");
  printf("-v, --verbose                      Be verbose.\n");
  printf("\n");
  printf("REMARK\n");
  printf("A reminder for commonly used prefixes.\n");
  printf("shost=                    Source hostname.\n");
  printf("src=                      Source IP address.\n");
  printf("suser=                    Source username.\n");
  printf("spt=                      Source port.\n");
  printf("dhost=                    Destination hostname.\n");
  printf("dst=                      Destination IP address.\n");
  printf("duser=                    Destination username.\n");
  printf("dpt=                      Destination port.\n");
  printf("csN=                      Custom string N.\n");
  printf("csNLabel=                 Label of custom string N.\n");
  printf("ahost=                    Agent hostname.\n");
  printf("agt=                      Agent IP address\n");
  printf("\n");
  printf("EXAMPLE\n");
  printf("%s --thread 32 suser=badguy | grep shost=owned\n", pname);
  printf("%s --start \"2000-04-23 3:13:37\" --end \"2000-04-23 7:33:13\" --basic-regexp duser=[^ ]*[aA][dD][mM][iI][nN]\n", pname);
  printf("\n");
  printf("NOTA\n");
  printf("Please do not report bugs.\n");
  printf("\n");
  exit(1);
}

arg_t
parse_args (int argc, char** argv){
  arg_t arg = {
    .start = 0,
    .end = 0,
    .path = &DEFAULT_PATH,
    .pattern = NULL,
    .pattern_len = 0,
    .out = stdout,
    .cflags = FIXED_STRING,
    .field = NULL,
    .field_len = 0,
  };
  pthread_mutex_init(&arg.out_mutex, NULL);
  static struct option long_options[] ={
    {"help",  no_argument, 0, 'h'},
    {"count",  no_argument, 0, 'c'},
    {"end",  required_argument, 0, 'e'},
    {"extended-regexp",  no_argument, 0, 'E'},
    {"fixed-string",  no_argument, 0, 'F'},
    {"field",  required_argument, 0, 'f'},
    {"basic-regexp",  no_argument, 0, 'G'},
    {"ignore-case",  no_argument, 0, 'i'},
    {"out",  required_argument, 0, 'o'},
    {"start",  required_argument, 0, 's'},
    {"thread",  required_argument, 0, 't'},
    {"verbose",  no_argument, 0, 'v'},
    {0, 0, 0, 0},
  };

  /* Parsing options */
  int c = 0, index = 0;
  while ( (c = getopt_long (argc, argv, "hce:EFf:Gio:s:t:v",long_options, &index)) != -1 ){
    switch (c){
    case 'c':{
      arg.out = NULL;
      break;
    }
    case 'E':{
      arg.cflags &= !(FIXED_STRING);
      arg.cflags |= REG_EXTENDED;
      break;
    }
    case 'e':{
      struct tm end;
      strptime (optarg, TIME_FMT, &end);
      arg.end = ((ullong)timegm (&end)) * 1000;
      break;
    }
    case 'F':{
      arg.cflags |= FIXED_STRING;
      break;
    }
    case 'f':{
      arg.field_len = strlen(optarg) + 2;
      arg.field = (char*)malloc((arg.field_len + 1)* sizeof(char));
      arg.field[0] = ' ';
      strcpy(arg.field + 1, optarg);
      arg.field[arg.field_len - 1] = '=';
      arg.field[arg.field_len] = 0;
      arg.field_bmGs = (int*)malloc(arg.field_len * sizeof(int));
      preBmGs(arg.field, arg.field_len, arg.field_bmGs);
      preBmBc(arg.field, arg.field_len, arg.field_bmBc);
      break;
    }
    case 'G':
      arg.cflags = 0;
      break;
    case 'o':
      arg.out = fopen (optarg, "wb");
      if (arg.out == NULL){
	fprintf (stderr, "Cannot open '%s': %s\n", optarg, strerror (errno));
	exit (1);
      }
      break;
    case 'i':{
      arg.cflags |= REG_ICASE;
      break;
    }
    case 's':{
      struct tm start;
      strptime (optarg, TIME_FMT, &start);
      arg.start = ((ullong)timegm (&start)) * 1000;
      break;
    }
    case 't':
      THREAD_NB = atoi(optarg);
      break;
    case 'v':
      VERBOSE_LEVEL = VERBOSE;
      break;
    default:
      printf ("unrecognized option -%c %s", c, optarg);
    case 'h':
      print_usage (argv[0]);
      break;
    }
  }     

  if (optind < argc){
    arg.pattern = argv[optind++];
    arg.pattern_len = strlen (arg.pattern);
    if ((arg.cflags & FIXED_STRING) != 0){
      arg.pattern_bmGs = (int*)malloc(arg.pattern_len * sizeof(int));
      preBmGs(arg.pattern, arg.pattern_len, arg.pattern_bmGs);
      preBmBc(arg.pattern, arg.pattern_len, arg.pattern_bmBc);
    }
  }
  if (optind < argc)
    arg.path = argv + (optind++);
  return arg;
}


int 
main (int argc, char** argv){
  arg_t arg = parse_args (argc, argv);
  struct stat statbuf;
  char** path, **end = argv +argc;
  for (path = arg.path; path < end; ++path){
  stat(*path, &statbuf);
  if (S_ISDIR(statbuf.st_mode))
    rsearch (*path, &arg);
  if (S_ISREG(statbuf.st_mode))
    do_search (*path, &arg);
  }
  if (arg.out == NULL)
    printf ("%llu\n", OUT_COUNT);
  if (arg.out != stdout && arg.out != NULL)
    fclose (arg.out);
  if (arg.pattern_bmGs != NULL)
    free (arg.field_bmGs);
  if (arg.field_bmGs != NULL){
    free (arg.field);
    free (arg.field_bmGs);
  }
  return 0;
}