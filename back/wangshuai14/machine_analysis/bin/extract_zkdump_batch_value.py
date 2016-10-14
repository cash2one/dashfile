#!/usr/bin/env python

import sys
import getopt
import json
import os
import zkdump_utils

def print_usage():
    print('extract_zkump_batch_value.py usage:')
    print('\t-h, --help: this help')
    print('\t-i, --input: zkdump file path, for example, /home/work/test.zkdump')
    print('\t-p, --path: path you want to extract from zkdump file, for example, /bs_se_0/app_spec')
    print('\t-k, --keys: keys you want to extract from specified path value, for example, --keys=/app_id,/package')
    print('\t--path_[1-40]: another path you want to extract from zkdump file, for example, /bs_se_0/app_spec')
    print('\t--keys_[1-40]: another keys you want to extract from specified path value, for example, --keys=/app_id,/package')
    print('\t-o, --output: output content, meta/kv/all')
# print_usage end

# main process begin
def main(argv):
    ext_path_num = 40
    short_param = 'hi:p:k:o:'
    long_param = ['help', 'input=', 'path=', 'keys=', 'output=']
    ex_path_param = []
    ex_keys_param = []
    for i in range(1, ext_path_num + 1):
        long_path = 'path_' + str(i) + '='
        long_keys = 'keys_' + str(i) + '='
        long_param.append(long_path)
        long_param.append(long_keys)

        ex_path = '--path_' + str(i)
        ex_keys = '--keys_' + str(i)
        ex_path_param.append(ex_path)
        ex_keys_param.append(ex_keys)

    try:
        opts, args = getopt.getopt(argv[1:], short_param, long_param)
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    input_mode = 'stdin_mode'
    extract_path = ''
    extract_keys = ''
    ex_extract_path_map = {}
    ex_extract_keys_map = {}
    output_content = 'kv'

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif o in ('-i', '--input'):
            input_mode = 'file_mode'
            zkdump_file_name = v
        elif o in ('-p', '--path'):
            extract_path = v
        elif o in ('-k', '--keys'):
            extract_keys = v
        elif o in (ex_path_param):
            ex_extract_path_map[o] = v
        elif o in (ex_keys_param):
            ex_extract_keys_map[o] = v
        elif o in ('-o', '--output'):
            output_content = v
        else:
            print 'unknown option'
            print_usage()
            sys.exit(1)

    extract_keys_list = extract_keys.split(',')
    if (extract_keys_list == ['']):
        extract_keys_list = []

    for key in ex_extract_keys_map.keys():
        on_ex_keys_list = ex_extract_keys_map[key].split(',')
        if (on_ex_keys_list == ['']):
            on_ex_keys_list = []
        ex_extract_keys_map[key] = on_ex_keys_list

    if (input_mode == 'stdin_mode'):
        zkdump_obj = zkdump_utils.load_zkdump_from_stdin()
    elif (input_mode == 'file_mode'):
        zkdump_obj = zkdump_utils.load_zkdump_from_file(zkdump_file_name)
    else:
        print 'input_mode unknown'
        print_usage()
        sys.exit(1)

    batch_meta_dict, batch_kv_dict = zkdump_utils.extract_zkdump_batch_value(zkdump_obj, \
    extract_path, extract_keys_list, \
    ex_extract_path_map, ex_extract_keys_map)
    if (batch_meta_dict == None) or (batch_kv_dict == None):
        print ('path %s or keys %s not found in zkdump file' %(extract_path, extract_keys))
        sys.exit(1)

    if (extract_keys == '' and ex_extract_keys_map == {}):
        output_content = 'meta'
    
    if (output_content == 'meta'):
        print (json.dumps(batch_meta_dict, indent = 4))
    elif (output_content == 'kv'):
        print (json.dumps(batch_kv_dict, indent = 4))
    elif (output_content == 'all'):
        print (json.dumps(batch_meta_dict, indent = 4))
        print (json.dumps(batch_kv_dict, indent = 4))
    else:
        print ('unknown output content: %s' %(output_content))
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)

