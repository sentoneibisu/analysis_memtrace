#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import datetime

def log(*args):
    msg = ' '.join(map(str, [datetime.datetime.now(), '>'] + list(args)))
    with open('log.txt', 'a') as f:
        f.write(msg + '\n')

def open_db(dbname='memref.db'):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cur = conn.cursor()
    return (conn, cur)

def close_db(conn):
    conn.close() 

def adjust_data(data, size):
    mask = 0xffffffff >> (32 - size * 8)
    return data & mask
