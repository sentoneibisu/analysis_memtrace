#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "cparse_memtrace.h"

#define MAX_FNAME 100


void enum_memtrace(FILE *fp);
void print_line(unsigned char* block);

unsigned long long j = 0;


int main(int argc, char *argv[])
{
    FILE *fp;
    char fname[MAX_FNAME] = {};

    if (argc != 2) {
        puts("USAGE: ./parse_memtrace <MEMTRACE_LOG>\n");
        exit(EXIT_FAILURE);
    }

    strncpy(fname, argv[1], MAX_FNAME - 1);
    fname[MAX_FNAME - 1] = '\0';

    if ((fp = fopen(fname, "rb")) == NULL){
        puts("[ERROR] File open error\n");
        exit(EXIT_FAILURE);
    }

    enum_memtrace(fp);
    fclose(fp);

    return 0;
}

void enum_memtrace(FILE *fp)
{
    unsigned char block[sizeof(mem_ref_t)] = {};
    unsigned long long i = 0;
    int c;

    while ((c = fgetc(fp)) != EOF) {
        block[i++ % sizeof(mem_ref_t)] = c;
        if ((i) % (sizeof(mem_ref_t)) == 0) {
            j++;
            print_line(block);
        }
    }
}


/* データベースに追加 */
void print_line(unsigned char* block)
{
    mem_ref_t new_memref;
    new_memref = *(mem_ref_t *)block;

    printf("[%lld] 0x%08x,%c,0x%08x,0x%x,0x%08x\n", j, new_memref.pc, (new_memref.write) ? 'w' : 'r', new_memref.size, new_memref.addr, new_memref.mem_data);
}
