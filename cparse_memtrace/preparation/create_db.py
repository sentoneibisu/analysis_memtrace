# coding: utf-8

import sqlite3

def create_db():
    dbname = 'memref.db'
    conn = sqlite3.connect('memref.db', isolation_level=None)
    cur = conn.cursor()
    schema_fname = 'memrefs_schema.sql'
    with open(schema_fname, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    return (conn, cur)


def Main():
    conn, cur = create_db()
    conn.close()


if __name__ == '__main__':
    Main()
