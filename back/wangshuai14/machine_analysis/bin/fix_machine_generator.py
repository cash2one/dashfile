#!/usr/bin/env python
#coding=utf-8

import getopt
import sys
import os
import ConfigParser
import json
import re
import time

def print_usage():
    print('fix_machine_generator.py usage:')
    print('\t-h, --help: print this help')
    print('\t-c, --config: config file, default conf/fix_machine_generator.conf')
    print('\t--unavailable: unavailable machine list with err_class')
    print('\t--no_running: no_running machine list with err_class')
    print('\t--usable: app usable')
    print('\t--total_machine_list: total machine list file, in json')
    print('\t--allret_ok: fix ok machine list from allret_beehive')
    print('\t--allret_err: err machine list from allret_beehive')
    print('\t--latest_fix_state: global latest machine fix state file')
    print('\t--new_fix_state: global new machine fix state file')

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

    conf_dict.update(get_value_dft(config, 'common', 'max_machine_ratio_to_fix', 1))
    conf_dict.update(get_value_dft(config, 'common', 'max_machine_num_to_fix', 10))

    conf_dict.update(get_value_dft(config, 'err_type_to_handle', 'type_num_total', 0))
    for i in range(1, conf_dict['type_num_total'] + 1):
        conf_dict.update(get_value_dft(config, 'err_type_to_handle', str(i) + 'th_err_to_handle', ''))

    return conf_dict

def init_config(conf_file):
    if (conf_file == ''):
        print('conf file can NOT be empty')
        print_usage_exit(1)

    conf_file = os.path.split(os.path.realpath(__file__))[0] + '/' + conf_file
    config = load_config(conf_file)
    config_dict = get_conf_value(config)

    return config_dict

def load_json_from_file(json_file_name, ignore_err = False):
    try:
        json_file = file(json_file_name)
    except IOError, err:
        if (ignore_err):
            return {}
        print str(err)
        print_usage_exit(1)

    try:
        json_obj = json.load(json_file)
    except json.ValueError, err:
        print str(err)
        print_usage_exit(1)

    json_file.close

    return json_obj

def app_usable_is_ok(machine_containers, machine_name, app_usable):
    if (app_usable == None):
        return True

    app_list = []
    for key in machine_containers.keys():
        if (re.match('.*_[0-9]*$', key) != None):
            app_name = key[0:key.rfind('_')]
            if app_name not in app_usable.keys():
                continue

            try:
                usable_shared_num = app_usable[app_name]['control_node']['usable']['shared_num']
                shared_instance_num = len(app_usable[app_name]['control_node']['usable'].keys()) - 1

                if (usable_shared_num - shared_instance_num <= 0):
                    instance_state =  app_usable[app_name][key]['status']['runtime']['run_state']
                    if (instance_state in ['RUNNING', 'NEW', 'REPAIR']):
                        return False
            except KeyError, err:
                return True

    return True

def get_machine_list(err_machine_list, err_type, app_usable):
    machine_list = []
    for key in err_machine_list.keys():
        if (err_machine_list[key]['ERR_CLASS'] == err_type):
            if (app_usable_is_ok(err_machine_list[key], key, app_usable)):
                machine_list.append(key)

    return machine_list

def update_machine_fix_state(state_node, target_state):
    timestamp = time.time()
    time_str = time.strftime('%Y-%m-%d-%H-%M',time.localtime(timestamp))

    if (target_state == 'init'):
        state_node['is_fixing'] = 'False'
        state_node['last_fixing_time'] = 'NONE'
        state_node['last_fixing_timestamp'] = 0
        state_node['last_fixed_time'] = 'NONE'
        state_node['last_fixed_timestamp'] = 0
    elif (target_state == 'fixing'):
        state_node['is_fixing'] = 'True'
        state_node['last_fixing_time'] = time_str
        state_node['last_fixing_timestamp'] = int(timestamp)
    elif (target_state == 'fixed'):
        state_node['is_fixing'] = 'False'
        state_node['last_fixed_time'] = time_str
        state_node['last_fixed_timestamp'] = int(timestamp)
    else:
        print('unkown target_state[%s]' %(target_state))
        print_usage_exit(1)

def set_fix_ok_state(allret_ok_machines, latest_fix_state):
    for machine in allret_ok_machines:
        if latest_fix_state['machine'].has_key(machine):
            if (latest_fix_state['machine'][machine]['is_fixing'] == 'True'):
                update_machine_fix_state(latest_fix_state['machine'][machine], 'fixed')
        else:
            sys.stderr.write('WARNING: machine[%s] in allret but not in fix_state, maybe new machine, please check!\n' %(machine))

def get_fixing_machine_list(allret_err_machines, latest_fix_state, total_machines):
    fixing_machine_list = get_machine_list(allret_err_machines, 'ERR_HANDLING_NOW', None)

    # double check, which machine to fix should be determined by me, not allret, except init time
    for machine in fixing_machine_list:
        if latest_fix_state['machine'].has_key(machine):
            if latest_fix_state['machine'][machine]['is_fixing'] == 'False':
                sys.stderr.write('WARNING: machine[%s]\'s state is handling in allret but False in fix_state, maybe init time, please check!\n' %(machine))
                update_machine_fix_state(latest_fix_state['machine'][machine], 'fixing')
        else:
            sys.stderr.write('WARNING: machine[%s]\'s state is handling in allret but NOT in fix_state, maybe init time, please check!\n' %(machine))
            latest_fix_state['machine'][machine] = {}
            update_machine_fix_state(latest_fix_state['machine'][machine], 'init')
            update_machine_fix_state(latest_fix_state['machine'][machine], 'fixing')

    # these machine is determined to fix before,but still not fixing
    should_fix_machine_list = []
    for machine in latest_fix_state['machine'].keys():
        if machine not in total_machines:
            del latest_fix_state['machine'][machine]
        elif latest_fix_state['machine'][machine]['is_fixing'] == 'True':
            if machine not in fixing_machine_list:
                should_fix_machine_list.append(machine)

    return fixing_machine_list, should_fix_machine_list

def update_latest_fix_state(total_machines, latest_fix_state, machine_to_fix):
    # update fix_state for all machines
    for machine in total_machines:
        if machine in latest_fix_state['machine'].keys():
            if machine in machine_to_fix:
                if (latest_fix_state['machine'][machine]['is_fixing'] == 'False'):
                    update_machine_fix_state(latest_fix_state['machine'][machine], 'fixing')
        else:
            sys.stderr.write('machine[%s] not in fix_state, maybe new machine, please check!\n' %(machine))
            # init this machine state
            latest_fix_state['machine'][machine] = {}
            update_machine_fix_state(latest_fix_state['machine'][machine], 'init')

            if machine in machine_to_fix:
                update_machine_fix_state(latest_fix_state['machine'][machine], 'fixing')

    # remove machine witch is in fix_state but not in total_machines
    total_machine_num = 0
    machine_in_fixing_num = 0
    old_total_machine_list = latest_fix_state['machine'].keys()[:]
    for machine in old_total_machine_list:
        if machine not in total_machines:
            del latest_fix_state['machine'][machine]
        else:
            total_machine_num += 1
            if latest_fix_state['machine'][machine]['is_fixing'] == 'True':
                machine_in_fixing_num += 1

    return total_machine_num, machine_in_fixing_num

def check_result(latest_fix_state, total_machine_num, total_machines, \
    machine_in_fixing_num, machine_num_to_fix, max_machine_num_to_fix):
    # check total fixing machine number at the same time
    if (total_machine_num != len(total_machines)):
        sys.stderr.write('FATAL: total_machine_num[%d] != len(total_machines)[%d], please check!\n' \
        %(total_machine_num, len(total_machines)))
        print_usage_exit(1)
    if (machine_in_fixing_num != machine_num_to_fix):
        sys.stderr.write('FATAL: machine_in_fixing_num[%d] != machine_num_to_fix[%d], please check!\n' \
        %(machine_in_fixing_num, machine_num_to_fix))
        print_usage_exit(1)
    if (machine_in_fixing_num > max_machine_num_to_fix):
        sys.stderr.write('WARNING: machine_in_fixing_num[%d] > max_machine_num_to_fix[%d], please check!\n' \
        %(machine_in_fixing_num, max_machine_num_to_fix))
        #print_usage_exit(1)

    latest_fix_state['total_machine_num'] = total_machine_num
    latest_fix_state['machine_in_fixing_num'] = machine_in_fixing_num

def generate_machines_to_fix(unavailable_machines, no_running_machines, app_usable, \
total_machines, allret_ok_machines, allret_err_machines, latest_fix_state, conf_value):
    total_machine_num = len(total_machines)
    max_machine_num_to_fix = conf_value['max_machine_ratio_to_fix'] * total_machine_num / 100
    if (max_machine_num_to_fix > conf_value['max_machine_num_to_fix']):
        max_machine_num_to_fix = conf_value['max_machine_num_to_fix']

    total_err_type_num = conf_value['type_num_total']
    err_list = []
    for i in range(1, total_err_type_num + 1):
        one_err_to_handle = conf_value[str(i) + 'th_err_to_handle']
        one_err = one_err_to_handle.split('.')
        err_list.append({\
        'where' : one_err[0], \
        'err_type' : one_err[1], \
        'check_usable' : one_err[2]})

    # init first time
    if (latest_fix_state == {}):
        latest_fix_state['machine'] = {}

    set_fix_ok_state(allret_ok_machines, latest_fix_state)
    fixing_machine_list, should_fix_machine_list = \
        get_fixing_machine_list(allret_err_machines, latest_fix_state, total_machines)

    machine_num_to_fix = len(fixing_machine_list) + len(should_fix_machine_list)
    machine_to_fix = []

    if (machine_num_to_fix > max_machine_num_to_fix):
        total_machine_num, machine_in_fixing_num = \
            update_latest_fix_state(total_machines, latest_fix_state, machine_to_fix)
        check_result(latest_fix_state, total_machine_num, total_machines, \
            machine_in_fixing_num, machine_num_to_fix, max_machine_num_to_fix)

        return machine_to_fix, should_fix_machine_list

    for i in range(0, total_err_type_num):
        if (err_list[i]['where'] == 'unavailable'):
            if (err_list[i]['check_usable'] == 'not_check_usable'):
                machine_list = get_machine_list(unavailable_machines, err_list[i]['err_type'], None)
            else:
                machine_list = get_machine_list(unavailable_machines, err_list[i]['err_type'], app_usable)
        elif (err_list[i]['where'] == 'no_running'):
            if (err_list[i]['check_usable'] == 'not_check_usable'):
                machine_list = get_machine_list(no_running_machines, err_list[i]['err_type'], None)
            else:
                machine_list = get_machine_list(no_running_machines, err_list[i]['err_type'], app_usable)
        else:
            print('unknown err source [%s]' %((err_list[i].keys())[0]))
            print_usage_exit(1)

        # make uniq
        filtered_machine_list = []
        for machine in machine_list:
            if machine not in machine_to_fix:
                filtered_machine_list.append(machine)
                if machine in should_fix_machine_list:
                    should_fix_machine_list.remove(machine)
                    machine_num_to_fix -= 1

        if (machine_num_to_fix + len(filtered_machine_list) > max_machine_num_to_fix):
            max_to_add = max_machine_num_to_fix - machine_num_to_fix
            machine_to_fix.extend(filtered_machine_list[0 : max_to_add])
            machine_num_to_fix += max_to_add

            break
        else:
            machine_to_fix.extend(filtered_machine_list)
            machine_num_to_fix += len(filtered_machine_list)

    total_machine_num, machine_in_fixing_num = \
        update_latest_fix_state(total_machines, latest_fix_state, machine_to_fix)
    check_result(latest_fix_state, total_machine_num, total_machines, \
        machine_in_fixing_num, machine_num_to_fix, max_machine_num_to_fix)

    return machine_to_fix, should_fix_machine_list

def main(argv):
    try:
        short_param = 'hc:'
        long_param = ['help', 'config=', 'unavailable=', 'no_running=', 'usable=', 'total_machine_list=', \
        'allret_ok=', 'latest_fix_state=', 'new_fix_state=', 'allret_err=']
        opts, args = getopt.getopt(argv[1:], short_param, long_param)
    except getopt.GetoptError, err:
        print str(err)
        print_usage_exit(1)

    conf_file = './conf/fix_machine_generator.conf'
    unavailable_machine_file = ''
    no_running_machine_file = ''
    app_usable_file = ''
    total_machine_list_file = 0
    allret_ok_file = ''
    allret_err_file = ''
    latest_fix_state_file = ''
    new_fix_state_file = ''

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage_exit(0)
        elif o in ('-c', '--config'):
            conf_file = v
        elif o in ('--unavailable'):
            unavailable_machine_file = v
        elif o in ('--no_running'):
            no_running_machine_file = v
        elif o in ('--usable'):
            app_usable_file = v
        elif o in ('--total_machine_list'):
            total_machine_list_file = v
        elif o in ('--allret_ok'):
            allret_ok_file = v
        elif o in ('--allret_err'):
            allret_err_file = v
        elif o in ('--latest_fix_state'):
            latest_fix_state_file = v
        elif o in ('--new_fix_state'):
            new_fix_state_file = v
        else:
            print ('unknown option [%s]' %(o))
            print_usage_exit(1)

    config_values = init_config(conf_file)

    if (unavailable_machine_file == '' or \
    no_running_machine_file == '' or \
    app_usable_file == '' or \
    total_machine_list_file == '' or \
    allret_ok_file == '' or \
    allret_err_file == '' or \
    latest_fix_state_file == '' or \
    new_fix_state_file == ''):
        print_usage_exit(1)

    unavailable_machines = load_json_from_file(unavailable_machine_file)
    no_running_machines = load_json_from_file(no_running_machine_file)
    app_usable = load_json_from_file(app_usable_file)
    total_machines = load_json_from_file(total_machine_list_file)['machine'].keys()
    allret_ok_machines = load_json_from_file(allret_ok_file)
    allret_err_machines = load_json_from_file(allret_err_file)
    latest_fix_state = load_json_from_file(latest_fix_state_file, ignore_err = True)

    machines_to_fix, machines_should_fix_ever_before = \
    generate_machines_to_fix(unavailable_machines['machine'], no_running_machines['machine'], \
    app_usable, total_machines, allret_ok_machines, allret_err_machines, latest_fix_state, config_values)

    for machine in machines_to_fix:
        print machine

    try:
        new_fix_state = file(new_fix_state_file, 'w')
    except IOError, err:
        print('open new_fix_state[%s] file failed' %(new_fix_state_file))
        print_usage_exit(1)

    new_fix_state.write(json.dumps(latest_fix_state, indent = 4))
    new_fix_state.close()

    try:
        should_fix_machine_filename = total_machine_list_file.split('.')[0] + '.machine.should_fix_ever_before.list'
        should_fix_machine_file = file(should_fix_machine_filename, 'w')
    except IOError, err:
        print('open should_fix_machine_file[%s] file failed' %(should_fix_machine_file))
        print_usage_exit(1)

    for machine in machines_should_fix_ever_before:
        should_fix_machine_file.write(machine + '\n')
    should_fix_machine_file.close()

if __name__ == '__main__':
    main(sys.argv)

