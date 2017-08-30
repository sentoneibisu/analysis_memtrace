#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sqlite3.h> 
#include "cparse_memtrace.h"

#define MAX_FNAME 100

void show_memtrace(memtrace_t *head);
void insert_memref(sqlite3 *db, char *errmsg, unsigned char* block);
void create_memtrace_db(FILE *fp, unsigned long long start);

unsigned long long j = 0;


int main(int argc, char *argv[])
{
    FILE *fp;
    char fname[MAX_FNAME] = {};

    if (argc != 3) {
        puts("USAGE: ./parse_memtrace <MEMTRACE_LOG> <START>\n");
        exit(EXIT_FAILURE);
    }

    strncpy(fname, argv[1], MAX_FNAME - 1);
    fname[MAX_FNAME - 1] = '\0';

    if ((fp = fopen(fname, "rb")) == NULL){
        puts("[ERROR] File open error\n");
        exit(EXIT_FAILURE);
    }

    create_memtrace_db(fp, atol(argv[2]));
    fclose(fp);
    return 0;
}

void create_memtrace_db(FILE *fp, unsigned long long start)
{
    sqlite3 *db; 
    char *errmsg; 
    unsigned char block[sizeof(mem_ref_t)] = {};
    //unsigned char c;
    int c;

    /* SQLite データベースを OPEN */ 
    sqlite3_open("memref.db", &db); 
    if (!db) { 
      exit(-1); 
    } 

    /* BEGIN TRANSACTION */ 
#ifdef USE_TRANSACTION 
    (void)sqlite3_exec(db, "BEGIN", NULL, NULL, &errmsg); 
#endif 
 
    unsigned long long i = 0;

    while ((c = fgetc(fp)) != EOF) {
        block[i++ % sizeof(mem_ref_t)] = c;
        if ((i) % (sizeof(mem_ref_t)) == 0) {
            j++;
            if (j-1 < start)
                continue;
            insert_memref(db, errmsg, block);
        }
    }

    /* COMMIT TRANSACTION */ 
#ifdef USE_TRANSACTION 
    (void)sqlite3_exec(db, "COMMIT", NULL, NULL, &errmsg); 
#endif 
    sqlite3_close(db); 
}


/* データベースに追加 */
void insert_memref(sqlite3 *db, char *errmsg, unsigned char* block)
{
    mem_ref_t new_memref;

    new_memref = *(mem_ref_t *)block;

    /******** SQL INSERT **********/
    char *sql; 

    printf("[%lld] 0x%08x,%c,0x%08x,0x%x,0x%08x\n", j, new_memref.pc, (new_memref.write) ? 'w' : 'r', new_memref.size, new_memref.addr, new_memref.mem_data);
    sql = sqlite3_mprintf("INSERT INTO memrefs (pc, write, size, addr, mem_data) VALUES (%d,%d,%d,%d,%d)", (int)new_memref.pc, 
                                                                                                           new_memref.write,
                                                                                                           (int)new_memref.size,
                                                                                                           (int)new_memref.addr,
                                                                                                           (int)new_memref.mem_data); 
    (void)sqlite3_exec(db, sql, NULL, NULL, &errmsg); 
#ifdef USE_TRANSACTION 
    if (j % 500000 == 0) {
        (void)sqlite3_exec(db, "COMMIT", NULL, NULL, &errmsg); 
        (void)sqlite3_exec(db, "BEGIN", NULL, NULL, &errmsg); 
    }
#endif 
    //free(new_memref);
}
