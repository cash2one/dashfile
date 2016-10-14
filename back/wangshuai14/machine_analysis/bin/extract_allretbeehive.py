#!/usr/bin/env python

import json
import sys
import getopt
import re

def print_usage():
    print('extract_allretbeehive.py usage:')
    print('\t-h, --help: this help')
    print('\t-m, --method: method to use, support gethostname/get_beehive_hostname/parse_reason')
    print('\t-p, --path: which node you want to extract, like fix_mac')
    print('\t-l, --machine_list: which machine list to parse_reason')
# print_usage end

def load_json_from_stdin():
    json_obj = json.load(sys.stdin)

    return json_obj
# load_json_from_stdin end

def load_json_from_file(json_file_name):
    json_file = file(json_file_name)
    json_obj = json.load(json_file)
    json_file.close

    return json_obj
# load_json_from_file end

def get_hostname_from_allretbeehive(json_obj, path, reason):
    (path_list, reason_list) = parse_path_reason(path, reason)
    
    hostname_list = []
    for index in range(0, len(path_list)):
        sub_class = path_list[index]
        sub_class_machines = json_obj[sub_class]
        if (type(sub_class_machines) != type([])):
            print('[%s] is not a list, cant extract hostname from this node' %(sub_class))
            print_usage()
            sys.exit(1)

        for one_machine in sub_class_machines:
            if (not one_machine.has_key('hostname')):
                print('extract hostname from machine error')
                print_usage()
                exit(1)

            if (in_reason(one_machine['reason'], reason_list[index])):
                hostname_list.append(one_machine['hostname'])

    return hostname_list

def parse_path_reason(path, reason):
    path_list = path.split(',')

    reason_list = reason.split(',')
    if (len(path_list) != len(reason_list)):
        print('path number is not eaqul to reason number')
        print_usage()
        exit(1)

    subreason_list = []
    for one_reason in reason_list:
        subreason = one_reason.split('|')
        subreason_list.append(subreason)

    return (path_list, subreason_list)

def in_reason(reason, reason_list):
    if (reason_list == ['ANY']):
        return True

    for r in reason_list:
        r_ext = '.*' + r + '.*'
        if (re.match(r_ext, reason) != None):
            return True

    return False

def get_beehive_hostname_from_allretbeehive(json_obj, path, reason):
    (path_list, reason_list) = parse_path_reason(path, reason)

    hostname_list = []
    for index in range(0, len(path_list)):
        sub_class = path_list[index]
        if (json_obj.has_key(sub_class)):
            sub_class_machines = json_obj[sub_class]
        else:
            continue

        if (type(sub_class_machines) != type([])):
            print('[%s] is not a list, cant extract hostname from this node' %(sub_class))
            print_usage()
            sys.exit(1)

        for one_machine in sub_class_machines:
            if (not one_machine.has_key('origin_primary_key')):
                print('extract beehive_hostname from machine error')
                print_usage()
                exit(1)

            if (in_reason(one_machine['reason'], reason_list[index])):
                hostname_list.append(one_machine['origin_primary_key'])

    return hostname_list

def extract_allretbeehive(json_obj, method, path, reason):
    if (method == 'gethostname'):
        result = get_hostname_from_allretbeehive(json_obj, path, reason)
    elif (method == 'get_beehive_hostname'):
        result = get_beehive_hostname_from_allretbeehive(json_obj, path, reason)
    else:
        print('method = [%s] not supported' %(method))
        print_usage()
        sys.exit(1)

    return result

def get_err_class(machine, machine_err_map):
    ERR_CLASS_MACHINE_UNREACHABLE = 'ERR_MACHINE_UNREACHABLE'
    ERR_CLASS_HOME_DISK_IO = 'ERR_HOME_DISK_IO'
    ERR_CLASS_SSD_IO = 'ERR_SSD_IO'
    ERR_CLASS_SSD_PARAM = 'ERR_SSD_PARAM'
    ERR_CLASS_SSD_DROP = 'ERR_SSD_DROP'
    ERR_CLASS_HOME_DROP = 'ERR_HOME_DROP'
    ERR_CLASS_FILE_IO = 'ERR_FILE_IO'
    ERR_CLASS_IN_ERROR_POOL = 'ERR_IN_ERROR_POOL'
    ERR_CLASS_MEMORY = 'ERR_MEMORY'
    ERR_CLASS_SOFT_ENV = 'ERR_SOFT_ENV'
    ERR_CLASS_HANDLING_NOW = 'ERR_HANDLING_NOW'
    ERR_CLASS_UNSPECIFIED = 'ERR_UNSPECIFIED'
    ERR_CLASS_UNKNOWN = 'ERR_UNKNOWN'
    err_class_dict = { \
        'ssh:cant' : ERR_CLASS_MACHINE_UNREACHABLE, \
        'DISKIO/home' : ERR_CLASS_HOME_DISK_IO, \
        'drop/ssd' : ERR_CLASS_SSD_DROP, \
        'mola' : ERR_CLASS_FILE_IO, \
        'search' : ERR_CLASS_FILE_IO, \
        'DISKIO/ssd' : ERR_CLASS_SSD_IO, \
        'in_cetus_err' : ERR_CLASS_IN_ERROR_POOL, \
        'agent' : ERR_CLASS_FILE_IO, \
        'drop/home' : ERR_CLASS_HOME_DROP, \
        'ssd_noatime' : ERR_CLASS_SSD_PARAM, \
        'flashv2drop' : ERR_CLASS_SSD_DROP, \
        'MemErr' : ERR_CLASS_MEMORY, \
        'ser_ok_mac_err' : ERR_CLASS_IN_ERROR_POOL, \
        'ip_local_port_range' : ERR_CLASS_SOFT_ENV, \
        'handovering' : ERR_CLASS_HANDLING_NOW, \
        'handling' : ERR_CLASS_HANDLING_NOW, \
        'some_ser_err' : ERR_CLASS_UNSPECIFIED, \
        'root_passwd' : ERR_CLASS_MACHINE_UNREACHABLE, \
        'ping:cant' : ERR_CLASS_MACHINE_UNREACHABLE, \
        'auth:cant' : ERR_CLASS_MACHINE_UNREACHABLE, \
        'flash3_softlink' : ERR_CLASS_SOFT_ENV, \
        'ssd_permission' : ERR_CLASS_SOFT_ENV, \
        'ssd_rotational' : ERR_CLASS_SSD_PARAM
    }

    if (machine_err_map.has_key(machine)):
        for key in err_class_dict.keys():
            key_ext = '.*' + key + '.*'
            if (re.match(key_ext, machine_err_map[machine]) != None):
                return err_class_dict[key]

    return ERR_CLASS_UNKNOWN

def generate_machine_err_map(allret_obj):
    err_map = {}

    for key in allret_obj:
        if type(allret_obj[key]) == type([]):
            for i in range(0, len(allret_obj[key])):
                if allret_obj[key][i].has_key('origin_primary_key') \
                and allret_obj[key][i].has_key('reason'):
                    if (allret_obj[key][i]['reason'] != ''):
                        err_map[allret_obj[key][i]['origin_primary_key']] = \
                        allret_obj[key][i]['reason']

    return err_map

def parse_reason(allret_obj, machine_list):
    machine_err_map = generate_machine_err_map(allret_obj)

    machine_err_reason = {}
    for machine in machine_list:
        err_class = get_err_class(machine, machine_err_map)
        machine_err_reason[machine] = {}
        machine_err_reason[machine]['ERR_CLASS'] = err_class

    return machine_err_reason


# main process begin
def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], \
        'hi:m:p:r:l:', ['help', 'input=', 'method=', 'path=', 'reason=', 'machine_list='])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    input_mode = 'stdin_mode'
    json_file_name = ''
    method = 'gethostname'
    path = ''
    reason = 'ANY'
    machine_list = ''

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif o in ('-i', '--input'):
            input_mode = 'file_mode'
            json_file_name = v
        elif o in ('-m', '--method'):
            method = v
        elif o in ('-p', '--path'):
            path = v
        elif o in ('-r', '--reason'):
            reason = v
        elif o in ('-l', '--machine_list'):
            machine_list = v
        else:
            print 'unknown option'
            print_usage()
            sys.exit(1)

    if (input_mode == 'stdin_mode'):
        json_obj = load_json_from_stdin()
    elif (input_mode == 'file_mode' and json_file_name != ''):
        json_obj = load_json_from_file(json_file_name)
    else:
        print 'input_mode unknown'
        print_usage()
        sys.exit(1)

    if (method not in ['gethostname', 'get_beehive_hostname', 'parse_reason']):
        print('method = [%s], error.' %(method))
        print_usage()
        sys.exit(1)

    if (method == 'parse_reason'):
        if (machine_list == ''):
            print('parse reason, please supply machine list to parse')
            print_usage()
            sys.exit(1)

        machine_list_obj = load_json_from_file(machine_list)

        result = parse_reason(json_obj, machine_list_obj)
    else:
        if (path == ''):
            print('you should specify which path to extract')
            print_usage()
            sys.exit(1)

        result = extract_allretbeehive(json_obj, method, path, reason)

    print(json.dumps(result, indent = 4))
    

if __name__ == '__main__':
    main(sys.argv)

