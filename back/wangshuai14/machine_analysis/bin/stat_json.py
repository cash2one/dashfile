#!/usr/bin/env python

import json
import sys
import getopt
import re

def print_usage():
    print('stat_json.py usage:')
    print('\t-h, --help: this help')
    print('\t-i, --input: json file path, for example, /home/work/test.json')
    print('\t-p, --path: json node path you want to stat, for example, /package/static_data')
    print('\t-m, --method: support count/list_uniq_value')
# print_usage end

def load_json_from_stdin():
    global json_obj
    json_obj = json.load(sys.stdin)
# load_json_from_stdin end

def load_json_from_file(json_file_name):
    json_file = file(json_file_name)
    
    global json_obj
    json_obj = json.load(json_file)
    
    json_file.close
# load_json_from_file end

def extract_json(json_path):
    slash_count = json_path.count('/')
    json_path_list = json_path.split('/')

    if (json_path == '/'):
        return json_obj
    
    if (slash_count == 0) or (json_path_list[0] != ''):
        print_usage()
        sys.exit(1)
    elif (json_path_list[len(json_path_list) - 1] == ''):
        slash_count = slash_count - 1
        del json_path_list[len(json_path_list) - 1]

    json_obj_tmp = json_obj
    for i in range(1, slash_count + 1):
        if (json_path_list[i] in json_obj_tmp.keys()):
            if (i == slash_count):
                return json_obj_tmp[json_path_list[i]]
            else:
                json_obj_tmp = json_obj_tmp[json_path_list[i]]
                continue
        else:
            print('path %s not found in json' %(json_path))
            return None

    return None
# extract_json end

def count_json(json_obj, path_list, level = 0):
    total_level = len(path_list)
    count = 0

    if (level >= total_level):
        return count

    for key in json_obj.keys():
        if (re.match(path_list[level], key) != None):
            if (level == total_level - 1):
                count += 1
            else:
                count += count_json(json_obj[key], path_list, level + 1)
        else:
            continue

    return count

def list_uniq_value_json(json_obj, path_list, level = 0, uniq_value_list = []):
    total_level = len(path_list)

    if (level >= total_level):
        return uniq_value_list

    for key in json_obj.keys():
        if (re.match(path_list[level], key) != None):
            if (level == total_level - 1):
                if json_obj[key].strip() not in uniq_value_list:
                    uniq_value_list.append(json_obj[key].strip())
            else:
                list_uniq_value_json(json_obj[key], path_list, level + 1, uniq_value_list)
        else:
            continue

    return uniq_value_list

def stat_json(json_obj, json_path, method):
    slash_count = json_path.count('/')
    json_path_list = json_path.split('/')

    if (json_path == '/'):
        print('can not stat root path')
        print_usage()
        sys.exit(1)
    
    if (slash_count == 0) or (json_path_list[0] != ''):
        print_usage()
        sys.exit(1)
    elif (json_path_list[len(json_path_list) - 1] == ''):
        slash_count = slash_count - 1
        del json_path_list[len(json_path_list) - 1]

    del json_path_list[0]

    if (method == 'count'):
        count = count_json(json_obj, json_path_list)
        print count
    elif (method == 'list_uniq_value'):
        uniq_value_list = list_uniq_value_json(json_obj, json_path_list)
        for uniq_value in uniq_value_list:
            print uniq_value
    else:
        print('method=[%s] not supported' %(method))
        print_usage()
        sys.exit(1)

# main process begin
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hi:p:m:', ['help', 'input=', 'path=', 'method='])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    input_mode = 'stdin_mode'
    json_path = '/'
    method = 'count'

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif o in ('-i', '--input'):
            input_mode = 'file_mode'
            json_file_name = v
        elif o in ('-p', '--path'):
            json_path = v
        elif o in ('-m', '--method'):
            method = v
        else:
            print 'unknown option'
            print_usage()
            sys.exit(1)

    if (input_mode == 'stdin_mode'):
        load_json_from_stdin()
    elif (input_mode == 'file_mode'):
        load_json_from_file(json_file_name)
    else:
        print 'input_mode unknown'
        print_usage()
        sys.exit(1)

    stat_json(json_obj, json_path, method)

if __name__ == '__main__':
    main(sys.argv)

