## メモリアクセストレース解析用

- メモリアクセストレースログをデータベースへ格納 (./cparse_memtrace)
```bash
$ ls
cparse_memtrace  create_db.py  memrefs_schema.sql  memtrace.AcroRd32.exe.*****.0000.log
$ python create_db.py
# 出力: 空のmemtrace.db
$ ls
cparse_memtrace  create_db.py  memrefs_schema.sql  memtrace.AcroRd32.exe.*****.0000.log  memref.db
$ ./cparse_memtrace memtrace.AcroRd32.exe.*****.0000.log 0

    .
    .
    .

$ sqlite3 memref.db
sqlite> select count(*) from memrefs;
20000000
sqlite> .q
$ ./cparse_memtrace memtrace.AcroRd32.exe.*****.0000.log 20000000

    .
    .
    .
# 入力: 空のmemref.db, memtraceログ
# 出力: パース完了後のmemref.db
```
- インデックスの作成
  - これをやらないと次の工程で時間がかかりすぎる
```bash
$ sqlite3 memref.db
sqlite> CREATE INDEX pcindex on memrefs(pc);
```

- メモリアクセスのグルーピングとJS文字列の探索
```bash
$ ls
create_functrace_db.py  functrace_schema.sql
$ python create_functrace_db.py
# 出力: 空のfunctrace.db

$ python grouping.py
# 入力: memref.db
# 出力: group.pickle, log.txt

$ python parse_functrace.py functrace.AcroRd32.exe*****.0000.log
# 入力: 空のfunctrace.db
# 出力: パース完了後のfunctrace.db

$ python search_js.py
# 必要に応じてsearch_js.py内でHard Codeしている探索対象のJS文字列を変更する
# 入力: group.pickle, functrace.db
# 出力: JS文字列を含んだメモリ領域の先頭周辺アドレス群(log.txtに出力される)

$ python enum_candidate_rvas.py
# 実行前にソースコード内のtarget_mem_addrsを上で得られたアドレス群に書き換える(適宜範囲を広げる)
# 入力: functrace.db, load_module_info_*****.txt
```

- その他のユーティリティー (./util)



