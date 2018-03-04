#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sqlite3
import pickle
import datetime
from collections import defaultdict
from tqdm import tqdm
from util import log, open_db, close_db

def debug(pc_aggr):
    log('len(pc_aggr):', len(pc_aggr))
    memtrace_sum = 0
    for x in pc_aggr:
        memtrace_sum += pc_aggr[x]
    log('memtrace_sum:', memtrace_sum)


def filter_pc(pc_aggr, threshold):
    filtered_pc_aggr = dict(filter(lambda x: x[1] > threshold, pc_aggr.items()))
    log('len(filtered_pc_aggr):', len(filtered_pc_aggr))
    return filtered_pc_aggr


def aggregate_pc(cur):
    """
    pc_aggr = {0x77ff4321: 8, 0x5322fa31: 105, 0x77aa00bc: 2, 
               0x77ff4322: 1, 0x5322fa32: 195, 0x77aa00bd: 4, 
               0x77ff4323: 9, 0x5322fa33: 100, 0x77aa00be: 3, 
               0x77ff4324: 2, 0x5322fa34: 105, 0x77aa00bf: 7, 
               0x77ff4325: 8, 0x5322fa35: 103, 0x77aa00c0: 9, ...}
    """
    pc_aggr = defaultdict(int)
    i = 1
    while True:
        cur.execute("select id, pc, addr from memrefs where id >= (?) and id <= (?)", (i, i + 10000) )
        i += 10000
        fetch_list = cur.fetchall()
        if fetch_list == []:
            break
        for id, pc, addr in fetch_list:
            print "%d,0x%08x,0x%08x" % (id, pc, addr)
            pc_aggr[pc] += 1
    return pc_aggr


def grouping(cur, pc_aggr, threshold):
    # all_groupsリストのフォーマット
    # [[id1, id2, id3, ...], [idM, idN, ...], ...]

    counter = 0
    all_groups = []
    for pc in tqdm(pc_aggr):
        counter += 1
        groups = []

        for write in xrange(2):
            cur.execute("select id, addr from memrefs where pc = (?) and write = (?)", (pc, write))
            record = cur.fetchone()
            if record == None:
                continue
            first_id = record[0]
            addr_base = record[1]
            cur_diff = 0
            group = [first_id]
            for id, addr in cur.fetchall():
                diff = addr - addr_base
                if diff == 1:
                    if cur_diff == 0:
                        cur_diff = 1
                        group.append(id)
                    elif cur_diff == 1:
                        group.append(id)
                    else:
                        if len(group) > threshold:
                            groups.append(group)
                        group = [id]
                        cur_diff = 0

                elif diff == 2:
                    if cur_diff == 0:
                        cur_diff = 2
                        group.append(id)
                    elif cur_diff == 2:
                        group.append(id)
                    else:
                        if len(group) > threshold:
                            groups.append(group)
                        group = [id]
                        cur_diff = 0

                elif diff == 4:
                    if cur_diff == 0:
                        cur_diff = 4
                        group.append(id)
                    elif cur_diff == 4:
                        group.append(id)
                    else:
                        if len(group) > threshold:
                            groups.append(group)
                        group = [id]
                        cur_diff = 0

                else:
                    if len(group) > threshold:
                        groups.append(group)
                    group = [id]
                    cur_diff = 0
                addr_base = addr
            if len(groups) != 0:
                log("[%d][0x%08x] group: %d" % (counter, pc, len(groups)))
                for g in groups:
                    all_groups.append(g)
    return all_groups

def Main():
    log('[+]', sys.argv[0])
    try:
        conn, cur = open_db()
        # pcごとに数を集計
        pc_aggr = aggregate_pc(cur)
        debug(pc_aggr)
    
        # グルーピング対象のPCを絞りこみ (数が101以上)
        pc_aggr = filter_pc(pc_aggr, threshold=100)
        debug(pc_aggr)

        # グルーピング (連続メモリアクセス数が51以上)
        groups = grouping(cur, pc_aggr, threshold=50)

    finally:
        with open('group.pickle', 'wb') as f:
            pickle.dump(groups, f)
        close_db(conn)


if __name__ == '__main__':
    Main()
