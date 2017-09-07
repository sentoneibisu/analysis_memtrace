## 全体の流れ
1. データベースの雛形を作成
2. cparse_memtrace.cのコンパイル
3. cparse_memtraceでデータベースに格納

## creat_db.py
### 説明
スキーマ(memrefs_schema.sql)を元にメモリアクセストレースログを格納するためのデータベースの雛形(memref.db)を作成 

## cparse_memtrace.c
### 説明
引数として与えられたメモリアクセストレースログを先頭から順番にパースし，memref.dbにインサートしていく．
- 引数1: パース対象のメモリアクセストレースログファイル
- 引数2: データベースに格納し始めるメモリアクセストレースのインデックス
  - 例えば，データベースに1000件のメモリアクセストレースが既に格納されていたら，引数2に1000を指定すると1000番目以降から挿入を始める

### コンパイル方法
```
$ gcc -DUSE_TRANSACTION -Wall -o cparse_memtrace cparse_memtrace.c -lsqlite3 -L /usr/lib/x86_64-linux-gnu/
```
-Lの後はlibsqlite3.soの場所を指定
なぜか-lsqlite3を後ろに書かないとコンパイルエラーになる．


