#!/usr/bin/env python

import json
import sys
import re

def load_zkdump_from_stdin():
    zkdump_obj = json.load(sys.stdin)
    return zkdump_obj
# load_zkdump_from_stdin end

def load_zkdump_from_file(zkdump_file_name):
    zkdump_file = file(zkdump_file_name)
    zkdump_txt = ''
    for line in zkdump_file:
        zkdump_txt = zkdump_txt + line
    zkdump_obj = json.loads(zkdump_txt.decode('utf-8', 'ignore'))
    zkdump_file.close
    return zkdump_obj
# load_zkdump_from_file end

def extract_zkdump(zkdump_obj, extract_path):
    zkdump_obj_sons = zkdump_obj['sons']
    zkdump_obj_meta = zkdump_obj['meta']

    slash_count = extract_path.count('/')
    extract_path_list = extract_path.split('/')

    if (extract_path == '/'):
        return (zkdump_obj_meta, zkdump_obj_sons)
    
    if (slash_count == 0) or (extract_path_list[0] != ''):
        print ('extract_key[%s] format error.' %(extract_path))
        sys.exit(1)
    elif (extract_path_list[len(extract_path_list) - 1] == ''):
        slash_count = slash_count - 1
        del extract_path_list[len(extract_path_list) - 1]

    for i in range(1, slash_count + 1):
        if (extract_path_list[i] in zkdump_obj_sons.keys()):
            if (i == slash_count):
                ##### to be modify, add key
                return (zkdump_obj_sons[extract_path_list[i]]['meta'], zkdump_obj_sons[extract_path_list[i]]['sons'])
            else:
                zkdump_obj_meta = zkdump_obj_sons[extract_path_list[i]]['meta']
                zkdump_obj_sons = zkdump_obj_sons[extract_path_list[i]]['sons']
                continue
        else:
            print('path %s not found in zkdump file' %(extract_path))
            return (1, 1)

    print('path %s not found in zkdump file' %(extract_path))
    return (1, 1)
# extract_zkdump end

def extract_value_from_metas(node_meta, extract_keys_list, match_result_kvs):
    for extract_key in extract_keys_list:
        slash_count = extract_key.count('/')
        extract_subkey_list = extract_key.split('/')

        if (extract_key == '/'):
            match_result_kvs[extract_key] = node_meta
            return
        
        if (slash_count == 0) or (extract_subkey_list[0] != ''):
            print ('extract_key[%s] format error.' %(extract_key))
            sys.exit(1)
        elif (extract_subkey_list[len(extract_subkey_list) - 1] == ''):
            slash_count = slash_count - 1
            del extract_subkey_list[len(extract_subkey_list) - 1]

        del extract_subkey_list[0]

        node_meta_tmp = node_meta
        match_result_kvs_tmp = match_result_kvs
        for i in range(0, slash_count):
            if (extract_subkey_list[i] in node_meta_tmp.keys()):
                if (i == slash_count - 1):
                    match_result_kvs_tmp[extract_subkey_list[i]] = node_meta_tmp[extract_subkey_list[i]]
                else:
                    node_meta_tmp = node_meta_tmp[extract_subkey_list[i]]
                    if (not match_result_kvs_tmp.has_key(extract_subkey_list[i])):
                        match_result_kvs_tmp[extract_subkey_list[i]] = {}
                    match_result_kvs_tmp = match_result_kvs_tmp[extract_subkey_list[i]]
                    continue
            else:
                for j in range(i, slash_count):
                    if (j == slash_count - 1):
                        match_result_kvs_tmp[extract_subkey_list[j]] = 'NOT_FOUND_IN_ORIGINAL_ZKDUMP'
                    else:
                        if (not match_result_kvs_tmp.has_key(extract_subkey_list[j])):
                            match_result_kvs_tmp[extract_subkey_list[j]] = {}
                        match_result_kvs_tmp = match_result_kvs_tmp[extract_subkey_list[j]]
                break

    return
# extract_value_from_metas end

def check_one_node(extract_path_list, i, slash_count, zkdump_obj_sons, extract_keys_list, match_result_metas, match_result_kvs):
    if (i >= slash_count):
        return

    for k in zkdump_obj_sons.keys():
        match = re.match(extract_path_list[i], k)
        if (match == None):
            continue

        if (not match_result_metas.has_key(k)):
            match_result_metas[k] = {}
        if (not match_result_kvs.has_key(k)):
            match_result_kvs[k] = {}
        if (i == slash_count - 1):
            match_result_metas[k] = zkdump_obj_sons[k]['meta']
            if (extract_keys_list != []):
                extract_value_from_metas(zkdump_obj_sons[k]['meta'], extract_keys_list, match_result_kvs[k])
        else:
            check_one_node(extract_path_list, i+1, slash_count, zkdump_obj_sons[k]['sons'], extract_keys_list, match_result_metas[k], match_result_kvs[k])

    return
# check_one_node end

def extract_one_path(zkdump_obj, path, keys_list, match_result_metas, match_result_kvs):
    slash_count = path.count('/')
    path_list = path.split('/')

    if (path == '/'):
        match_result_metas[path] = zkdump_obj['meta']
        if (keys_list != []):
            match_result_kvs = extract_value_from_metas(path, zkdump_obj['meta'], keys_list, match_result_kvs)
        return
    
    if (slash_count == 0) or (path_list[0] != ''):
        print ('extract_key[%s] format error.' %(path))
        sys.exit(1)
    elif (path_list[len(path_list) - 1] == ''):
        slash_count = slash_count - 1
        del path_list[len(path_list) - 1]
    
    # delete '' in the front of path_list, so that len(path_list) == slash_count
    del path_list[0]

    check_one_node(path_list, 0, slash_count, zkdump_obj['sons'], keys_list, match_result_metas, match_result_kvs)

    return

def extract_zkdump_batch_value(zkdump_obj, extract_path, extract_keys_list, \
ex_extract_path_map, ex_extract_keys_map):
    match_result_metas = {}
    match_result_kvs = {}

    if (extract_path != ''):
        extract_one_path(zkdump_obj, extract_path, extract_keys_list, match_result_metas, match_result_kvs)

    for path in ex_extract_path_map.keys():
        ex_extract_path = ex_extract_path_map[path]
        ex_extract_keys_list = []
        path_no = path.split('_')[1]
        if ex_extract_keys_map.has_key('--keys_' + path_no):
            ex_extract_keys_list = ex_extract_keys_map['--keys_' + path_no]

        if (ex_extract_path != ''):
            extract_one_path(zkdump_obj, ex_extract_path, ex_extract_keys_list, match_result_metas, match_result_kvs)

    return (match_result_metas, match_result_kvs)
# extract_zkdump end

