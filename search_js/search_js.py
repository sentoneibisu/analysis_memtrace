#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import pickle
import struct
import cStringIO
from tqdm import tqdm

def open_db():
    #conn = sqlite3.connect('memref.db', isolation_level=None)
    conn = sqlite3.connect('memref.db')
    cur = conn.cursor()
    return (conn, cur)

def close_db(conn):
    conn.close() 

def adjust_data(data, size):
    mask = 0xffffffff >> (32 - size * 8)
    return data & mask

def search_js():
    embedded_js = '''//appleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleappleapple    app.alert("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq");'''
    try:
        conn, cur = open_db()
        with open('group.pickle', 'rb') as f:
            group = pickle.load(f)

        for i, g in enumerate(tqdm(group)):
            ascii_data = cStringIO.StringIO()
            ids = tuple(g)
            sqlstr = "select id, addr, size, mem_data from memrefs where id in %s" % str(ids)
            cur.execute(sqlstr)
            for id, addr, size, mem_data in tqdm(cur.fetchall()):
                mem_data = struct.pack('<I', adjust_data(mem_data, size))
                if any([31 < ord(x) < 127 for x in mem_data]):
                    for x in mem_data:
                        if 31 < ord(x) < 127:
                            ascii_data.write(x)
            if embedded_js in ascii_data.getvalue():
                print "Group including JavaScript: %d" % i
                cur.execute("select id, addr, size, mem_data from memrefs where id in (?,?,?)", (g[0], g[1], g[2]))
                for id, addr, size, mem_data in cur.fetchall():
                    print "    [{0}] 0x{1:08x},{2},0x{3:08x}".format(id, addr, size, mem_data)
    

    finally:
        close_db(conn)


if __name__ == '__main__':
    search_js()
