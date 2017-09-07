CC = gcc
CFLAGS = -Wall -I../include -DUSE_TRANSACTION -lsqlite3 -L /usr/lib/x86_64-linux-gnu/

cparse_memtrace: cparse_memtrace.c
	$(CC) -o $@ $< $(CFLAGS)
