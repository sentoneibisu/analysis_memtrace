#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sqlite3
from collections import defaultdict
from util import open_db, close_db

class ModuleInfo(object):
    def __init__(self, full_path, start, ep, end, size):
        self.full_path = full_path
        self.name      = full_path.split('\\')[-1]
        self.start     = start
        self.ep        = ep
        self.end       = end
        self.size      = size

    def calc_rva(self, addr):
        return addr - self.start

def parse_load_module_info(file_name):
    """Parse a load module informations log.
    Arguments
    ---------
    file_name (str) : 対象ファイル名

    Returns
    -------
    module_infos (list) : ロードモジュール情報ディクショナリのリスト
                          [{'full_path': full_path1, 
                            'start'    : start1, 
                            'ep'       : ep1,
                            'end'      : end1,
                            'size'     : size1}, ...]

    """

    module_infos = []
    pfull_path  = re.compile(r'full_path\s*: (.*)')
    pstart      = re.compile(r'start\s*: (.*)')
    pentry_point = re.compile(r'entry_point\s*: (.*)')
    pend        = re.compile(r'end\s*: (.*)')
    pmodule_internal_size = re.compile(r'module_internal_size\s*: (.*)')
    with open(file_name, 'r') as f:
        module_info = {}
        for line in f:
            if pfull_path.match(line):
                module_info['full_path'] = pfull_path.match(line).group(1).strip()
            elif pstart.match(line):
                module_info['start'] = int(pstart.match(line).group(1).strip(), 16)
            elif pentry_point.match(line):
                module_info['ep'] = int(pentry_point.match(line).group(1).strip(), 16)
            elif pend.match(line):
                module_info['end'] = int(pend.match(line).group(1).strip(), 16)
            elif pmodule_internal_size.match(line):
                module_info['size'] = int(pmodule_internal_size.match(line).group(1).strip(), 16)
            else:
                module_infos.append(module_info)
                module_info = {}
    return module_infos


def get_rvas(candidate_funcs, module_infos):
    """Get RVAs (function offset) of each modules.
    Arguments
    ---------
    candidate_funcs (list) : 候補関数と引数番号のタプルのリスト
                             [(addr1, arg_num1), (addr2, arg_num2), ...]

    module_infos (list) : ロードモジュール情報ディクショナリのリスト
                          [{'full_path': full_path1, 
                            'start'    : start1, 
                            'ep'       : ep1,
                            'end'      : end1,
                            'size'     : size1}, ...]

    Returns
    -------
    {name1: [(rva1, arg_num1), (rva2, arg_num2), ...], 
     name2: [(rvaX, arg_numX), (rvaY, arg_numY), ...], ...}
    """
    module_rvas = defaultdict(list)
    for module_info in module_infos:
        m = ModuleInfo(**module_info)
        for candidate_func in candidate_funcs:
            addr, arg_num = candidate_func
            if m.start <= addr <= m.end:
                module_rvas[m.name].append((m.calc_rva(addr), arg_num))
    return module_rvas


def get_candidate_funcs(target_mem_addrs):
    """Get candidate functions for extract JavaScript codes.
    Arguments
    ---------
    target_mem_addrs (tuple) : JS文字列を含んだメモリ領域の先頭周辺アドレス群

    Returns
    -------
    candidate_funcs (list) : 候補関数と引数番号のタプルのリスト
                             [(addr1, arg_num1), (addr2, arg_num2), ...]
    """
    try:
        dbname = 'functrace.db'
        conn, cur = open_db(dbname=dbname)

        query = "select addr, arg1, arg2, arg3 from functraces where (arg1 in {0}) or (arg2 in {0}) or (arg3 in {0})" \
                 .format(str(target_mem_addrs))
        cur.execute(query)
        func_addrs = [] 
        candidate_funcs= []
        for addr, arg1, arg2, arg3 in cur.fetchall():
            if addr not in func_addrs:
                func_addrs.append(addr)
                if arg1 in target_mem_addrs:
                    candidate_funcs.append((addr, 1))
                elif arg2 in target_mem_addrs:
                    candidate_funcs.append((addr, 2))
                elif arg3 in target_mem_addrs:
                    candidate_funcs.append((addr, 3))
    finally:
        close_db(conn)
    return candidate_funcs

def main():
    target_mem_addrs = (0x115f77ff, 0x115f7800, 0x115f7801, 0x115f7802, 0x115f7803,
                        0x0eacad8f, 0x0eacad90, 0x0eacad91, 0x0eacad92, 0x0eacad93,
                        0x1172600e, 0x1172600f, 0x11726010, 0x11726011, 0x11726012, 
                        0x114ba476, 0x114ba477, 0x114ba478, 0x114ba479, 0x114ba47a)
    candidate_funcs = get_candidate_funcs(target_mem_addrs)
    module_infos = parse_load_module_info('load_module_info_09064.txt')
    result = get_rvas(candidate_funcs, module_infos)

    for mod in result:
        print "[+] {0}".format(mod)
        for rva, arg_num in result[mod]:
            print "  0x{0:08x} : {1}".format(rva, arg_num)

if __name__ == '__main__':
    main()
