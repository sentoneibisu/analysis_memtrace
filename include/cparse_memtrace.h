#ifndef _CPARSE_MEMTRACE_H
#define _CPARSE_MEMTRACE_H

typedef struct {
    int  write;
    int  addr;
    int size;
    int pc;
    int mem_data;
} mem_ref_t;

typedef struct {
    mem_ref_t *mem_ref;
    struct memtrace_t *next;
} memtrace_t;


#endif
