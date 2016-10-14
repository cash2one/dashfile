#!/usr/bin/env python

import json
import sys
import getopt
import re

def print_usage():
    print('compute_json.py usage:')
    print('\t-h, --help: this help')
    print('\t--f1: first json file')
    print('\t--p1: node path in first json file')
    print('\t--f2: second json file')
    print('\t--p2: node path in second json file')
    print('\t-m, --method: can only be join/include_filter/exlude_filter')
# print_usage end

def load_json_from_file(json_file_name):
    json_file = file(json_file_name)
    json_obj = json.load(json_file)
    json_file.close

    return json_obj
# load_json_from_file end

def parse_json_path(json_path):
    slash_count = json_path.count('/')
    path_list = json_path.split('/')

    if (json_path == '/'):
        return []
    
    if (slash_count == 0) or (path_list[0] != ''):
        print ('json_path[%s] format error.' %(json_path))
        print_usage()
        sys.exit(1)
    elif (path_list[len(path_list) - 1] == ''):
        slash_count = slash_count - 1
        del path_list[len(path_list) - 1]

    del path_list[0]

    return path_list

def get_to_be_filter_list(json_obj, path_list, filter_kvs_dict, level = 0):
    if (path_list == []):
        if (type(json_obj) == type([])):
            for i in range(0, len(json_obj)):
                filter_kvs_dict[json_obj[i]] = json_obj[i]
        else:
            filter_kvs_dict.update(json_obj)
        return

    if (level >= len(path_list)):
        return

    for key in json_obj.keys():
        if (re.match(path_list[level], key) != None):
            if (level == len(path_list) - 1):
                if (type(json_obj[key]) == type({})):
                    filter_kvs_dict.update(json_obj[key])
                else:
                    # here use value to be key
                    filter_kvs_dict[json_obj[key]] = json_obj[key]
            else:
                get_to_be_filter_list(json_obj[key], path_list, filter_kvs_dict, level + 1)
        else:
            continue

def do_nothing():
    return

def filter_json(json_obj, path_list, filter_kvs_dict, method, level = 0):
    filter_keys = filter_kvs_dict.keys()

    if (path_list == []):
        if (type(json_obj) == type({})):
            for key in json_obj.keys():
                if (method == 'join'):
                    if key not in filter_keys:
                        #del json_obj[key]
                        do_nothing()
                    else:
                        json_obj[key].update(filter_kvs_dict[key])
                elif (method == 'include_filter'):
                    if key not in filter_keys:
                        del json_obj[key]
                elif (method == 'exlude_filter'):
                    if key in filter_keys:
                        del json_obj[key]
                else:
                    print('impossible')
                    print_usage()
                    sys.exit(1)
        # is list
        else:
            # must copy another list to iterate
            key_list = list(json_obj)
            for key in key_list:
                if (method == 'join'):
                    print('can not join with lists')
                    print_usage()
                    sys.exit(1)
                elif (method == 'include_filter'):
                    if key not in filter_keys:
                        index = json_obj.index(key)
                        del json_obj[index]
                elif (method == 'exlude_filter'):
                    if key in filter_keys:
                        index = json_obj.index(key)
                        del json_obj[index]
                else:
                    print('impossible')
                    print_usage()
                    sys.exit(1)

    if (level >= len(path_list)):
        return

    for key in json_obj.keys():
        if (re.match(path_list[level], key) != None):
            if (level == len(path_list) - 1):
                for target_key in json_obj[key].keys():
                    if (method == 'join'):
                        if target_key not in filter_keys:
                            #del json_obj[key][target_key]
                            do_nothing()
                        else:
                            json_obj[key][target_key].update(filter_kvs_dict[target_key])
                    elif (method == 'include_filter'):
                        if target_key not in filter_keys:
                            del json_obj[key][target_key]
                    elif (method == 'exlude_filter'):
                        if target_key in filter_keys:
                            del json_obj[key][target_key]
                    else:
                        print('impossible')
                        print_usage()
                        sys.exit(1)
            else:
                filter_json(json_obj[key], path_list, filter_kvs_dict, method, level + 1)
        else:
            continue
        
# main process begin
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hm:', ['f1=', 'p1=', 'f2=', 'p2=', 'method='])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    json_file1 = ''
    node_path1 = ''
    json_file2 = ''
    node_path2 = ''
    method = 'join'

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif o in ('-m', '--method'):
            method = v
        elif o in ('--f1'):
            json_file1 = v
        elif o in ('--p1'):
            node_path1 = v
        elif o in ('--f2'):
            json_file2 = v
        elif o in ('--p2'):
            node_path2 = v
        else:
            print 'unknown option'
            print_usage()
            sys.exit(1)

    if (method not in ['join', 'include_filter', 'exlude_filter']):
        print('method=[%s] error' %(method))
        print_usage()
        sys.exit(1)
    if (json_file1 == '' or node_path1 == '' \
    or json_file2 =='' or node_path2 == ''):
        print('file or path can not be empty')
        print_usage()
        sys.exit(1)
    
    json_obj1 = load_json_from_file(json_file1)
    json_obj2 = load_json_from_file(json_file2)

    path_list_2 = parse_json_path(node_path2)
    filter_kvs_dict = {}
    get_to_be_filter_list(json_obj2, path_list_2, filter_kvs_dict)

    path_list_1 = parse_json_path(node_path1)
    filter_json(json_obj1, path_list_1, filter_kvs_dict, method)
    print json.dumps(json_obj1, indent = 4)
    

if __name__ == '__main__':
    main(sys.argv)

