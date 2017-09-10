#!/usr/bin/env python
# coding: utf-8
import sqlite3

def create_db(dbname='functrace.db'):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cur = conn.cursor()
    schema_fname = 'functrace_schema.sql'
    with open(schema_fname, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    return (conn, cur)


def Main():
    conn, cur = create_db()
    conn.close()


if __name__ == '__main__':
    Main()
