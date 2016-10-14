#!/usr/bin/env python
#coding=utf-8

import getopt
import sys
import os
import ConfigParser
import json
import re

def print_usage():
    print('machine_state_generator.py usage:')
    print('\t-h, --help: print this help')
    print('\t-c, --config: config file, default conf/machine_state_generator.conf')
    print('\t-m, --method: gen_online/gen_offline flag')
    print('\t--cur_online: machine list with state online at current')
    print('\t--cur_offline: machine list with state offline at current')
    print('\t--allret_ok: machine list with state ok in allret_beehive file')
    print('\t--allret_err: machine list with state err in allret_beehive file')
    print('\t--total_machine_num: total machine number of cluster')

    return

def print_usage_exit(ret_code = 0):
    print_usage()
    sys.exit(ret_code)

def load_config(conf_file):
    conf_parser = ConfigParser.ConfigParser()
    if (conf_parser.read(conf_file) == []):
        print('can not read [%s]' %(conf_file))
        print_usage_exit(1)

    return conf_parser

def get_value_dft(config, section, key, dft_value):
    value_type = type(dft_value)

    try:
        if (value_type == type('str')):
            value = config.get(section, key)
        elif (value_type == type(0)):
            value = config.getint(section, key)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # TODO, need log
        value = dft_value

    return {key:value}

def get_conf_value(config):
    conf_dict = {}

    conf_dict.update(get_value_dft(config, 'common', 'max_offline_machine_ratio', 10))
    conf_dict.update(get_value_dft(config, 'common', 'max_offline_machine_num', 200))

    conf_dict.update(get_value_dft(config, 'err_type_to_set_offline', 'type_num_total', 0))
    for i in range(1, conf_dict['type_num_total'] + 1):
        conf_dict.update(get_value_dft(config, 'err_type_to_set_offline', str(i) + 'th_err_to_set', ''))

    return conf_dict

def init_config(conf_file):
    if (conf_file == ''):
        print('conf file can NOT be empty')
        print_usage_exit(1)

    conf_file = os.path.split(os.path.realpath(__file__))[0] + '/' + conf_file
    config = load_config(conf_file)
    config_dict = get_conf_value(config)

    return config_dict

def load_json_from_file(json_file_name):
    try:
        json_file = file(json_file_name)
    except IOError, err:
        print str(err)
        print_usage_exit(1)

    try:
        json_obj = json.load(json_file)
    except json.ValueError, err:
        print str(err)
        print_usage_exit(1)

    json_file.close

    return json_obj

def gen_online_list(cur_offline_file, allret_ok_file):
    if (cur_offline_file == '' or allret_ok_file == ''):
        print('offline and allret_ok file needed to gen online list')
        print_usage_exit(1)

    cur_offline_machines = load_json_from_file(cur_offline_file)['machine'].keys()
    allret_ok_machines = load_json_from_file(allret_ok_file)

    machines_to_set_online = []
    for machine in allret_ok_machines:
        if machine in cur_offline_machines:
            machines_to_set_online.append(machine)

    return machines_to_set_online

def gen_offline_list(cur_online_file, allret_err_file, total_machine_num, config_values):
    if (cur_online_file == '' or allret_err_file == '' or total_machine_num == 0):
        print('online and allret_err and total_machine_num needed to gen offline list')
        print_usage_exit(1)

    max_num_to_set_offline = total_machine_num * config_values['max_offline_machine_ratio'] / 100
    if (max_num_to_set_offline > config_values['max_offline_machine_num']):
        max_num_to_set_offline = config_values['max_offline_machine_num']

    cur_online_machines = load_json_from_file(cur_online_file)['machine'].keys()
    allret_err_machines = load_json_from_file(allret_err_file)

    machines_to_set_offline = []
    machines_to_set_offline_num = 0
    for err_type_index in range(1, config_values['type_num_total'] + 1):
        err_type = config_values[str(err_type_index) + 'th_err_to_set']
        for machine in allret_err_machines.keys():
            if (allret_err_machines[machine]['ERR_CLASS'] == err_type):
                if machine in cur_online_machines:
                    if ((machines_to_set_offline_num + 1) <= max_num_to_set_offline):
                        machines_to_set_offline.append(machine)
                        machines_to_set_offline_num += 1
                    else:
                        break
        if (machines_to_set_offline_num > max_num_to_set_offline):
            break
    
    return machines_to_set_offline

def main(argv):
    try:
        short_param = 'hc:m:'
        long_param = ['help', 'config=', 'method=', 'cur_offline=', 'cur_online=', 'allret_ok=', 'allret_err=', 'total_machine_num=']
        opts, args = getopt.getopt(argv[1:], short_param, long_param)
    except getopt.GetoptError, err:
        print str(err)
        print_usage_exit(1)

    conf_file = './conf/machine_state_generator.conf'
    method = ''
    cur_offline_file = ''
    cur_online_file = ''
    allret_ok_file = ''
    allret_err_file = ''
    total_machine_num = 0

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage_exit(0)
        elif o in ('-c', '--config'):
            conf_file = v
        elif o in ('-m', '--method'):
            method = v
        elif o in ('--cur_offline'):
            cur_offline_file = v
        elif o in ('--cur_online'):
            cur_online_file = v
        elif o in ('--allret_ok'):
            allret_ok_file = v
        elif o in ('--allret_err'):
            allret_err_file = v
        elif o in ('--total_machine_num'):
            total_machine_num = int(v)
        else:
            print ('unknown option [%s]' %(o))
            print_usage_exit(1)

    if (method == ''):
        print('method cannot be empty')
        print_usage_exit(1)

    if (method == 'gen_online'):
        machine_list = gen_online_list(cur_offline_file, allret_ok_file)
    elif (method == 'gen_offline'):
        config_values = init_config(conf_file)
        machine_list = gen_offline_list(cur_online_file, allret_err_file, total_machine_num, config_values)
    else:
        print('method=[%s] unknown' %(method))
        print_usage_exit(1)

    for machine in machine_list:
        print machine

if __name__ == '__main__':
    main(sys.argv)

