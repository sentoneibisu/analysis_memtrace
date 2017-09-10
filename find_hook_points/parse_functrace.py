#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import sqlite3
from tqdm import tqdm
from util import open_db, close_db

def insert_record(cur, url):
    cur.execute("insert into pdfs (url, add_date) values (?, ?)", (url, current_time))

def main():
    dbname = 'functrace.db'
    conn, cur = open_db(dbname=dbname, use_autocommit=False)

    if len(sys.argv) != 2:
        print "USAGE: {0} <FUNCTRACE_LOG>".format(sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        for line in tqdm(f):
            pfunc = re.compile(r'\[(0x[a-f0-9]+)\](0x[a-f0-9]+),(0x[a-f0-9]+),(0x[a-f0-9]+)')
            mfunc = pfunc.match(line)
            func_info = [int(x, 16) for x in mfunc.groups()]
            conn.execute('insert into functraces (addr, arg1, arg2, arg3) values(?, ?, ?, ?)', tuple(func_info))
    conn.commit()

if __name__ == '__main__':
    main()
