#!/usr/bin/env python
#coding=utf-8

import json
import sys
import getopt
import re

def print_usage():
    print('analyse_json.py usage:')
    print('\t-h, --help: this help')
    print('\t-i, --input: json file path, for example, /home/work/test.json')
    print('\t-m, --method: can only be and/or')
    print('\t-e, --expr: expresion you want to analyse from json, for example, /bs.*/hostname=a.*,/bs.*/run_state=RUNNING')
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

def parse_json_path(path):
    if (path == '/'):
        print ('json path[%s] format error.' %(path))
        print_usage()
        sys.exit(1)
    
    slash_count = path.count('/')
    path_node_list = path.split('/')

    if (slash_count == 0) or (path_node_list[0] != ''):
        print ('json path[%s] format error.' %(path))
        print_usage()
        sys.exit(1)
    elif (path_node_list[len(path_node_list) - 1] == ''):
        slash_count = slash_count - 1
        del path_node_list[len(path_node_list) - 1]
    
    # delete '' in the front of path_node_list, so that len(path_node_list) == slash_count
    del path_node_list[0]
    return path_node_list

def parse_sub_expr(sub_expr, sub_expr_kv):
    if (sub_expr.find('==') != -1):
        kv = sub_expr.split('==')
        op = '=='
    elif (sub_expr.find('!=') != -1):
        kv = sub_expr.split('!=')
        op = '!='
    elif (sub_expr.find('>=') != -1):
        kv = sub_expr.split('>=')
        op = '>='
    elif (sub_expr.find('>') != -1):
        kv = sub_expr.split('>')
        op = '>'
    elif (sub_expr.find('<=') != -1):
        kv = sub_expr.split('<=')
        op = '<='
    elif (sub_expr.find('<') != -1):
        kv = sub_expr.split('<')
        op = '<'
    elif (sub_expr.find('.MATCH.') != -1):
        kv = sub_expr.split('.MATCH.')
        op = '.MATCH.'
    elif (sub_expr.find('.NOT_MATCH.') != -1):
        kv = sub_expr.split('.NOT_MATCH.')
        op = '.NOT_MATCH.'
    elif (sub_expr.find('.CONTAIN.') != -1):
        kv = sub_expr.split('.CONTAIN.')
        op = '.CONTAIN.'
    elif (sub_expr.find('.NOT_CONTAIN.') != -1):
        kv = sub_expr.split('.NOT_CONTAIN.')
        op = '.NOT_CONTAIN.'
    elif (sub_expr.find('.HAS_CHILDREN.') != -1):
        kv = sub_expr.split('.HAS_CHILDREN.')
        op = '.HAS_CHILDREN.'
    elif (sub_expr.find('.NOT_HAS_CHILDREN.') != -1):
        kv = sub_expr.split('.NOT_HAS_CHILDREN.')
        op = '.NOT_HAS_CHILDREN.'
    else:
        print 'unkown expresion: '+sub_expr
        print_usage()
        sys.exit(1)

    if (kv[0] == ''):
        print ('sub_expr [%s] format error' %(sub_expr))
        print_usage()
        sys.exit(1)
    
    path_node_list = []
    path_node_list = parse_json_path(kv[0])
    sub_expr_kv['path_node_list'] = path_node_list
    sub_expr_kv['value'] = kv[1]
    sub_expr_kv['operator'] = op

def parse_expr(expr):
    sub_expr = expr.split(',')
    if (sub_expr[0] == ''):
        print ('expresion [%s] format error.' %(expr))
        print_usage()
        sys.exit(1)
    if (sub_expr[len(sub_expr) - 1] == ''):
        del sub_expr[len(sub_expr) - 1]

    sub_expr_kv = []
    for i in range(0, len(sub_expr)):
        sub_expr_kv.insert(i, {})
        parse_sub_expr(sub_expr[i], sub_expr_kv[i])

    return sub_expr_kv

def to_digit_if_is_digit(obj):
    if (type(obj) == type(1)):
        return (True, obj)
    elif ((type(obj) == type('1')) and obj.isdigit()):
        return (True, int(obj))
    else:
        return (False, -1)

def compair(obj1, obj2, operator):
    if (operator in ['==', '!=', '>=', '>', '<=', '<']):
        (is_int_obj1, int_obj1) = to_digit_if_is_digit(obj1)
        (is_int_obj2, int_obj2) = to_digit_if_is_digit(obj2)
        if ((not is_int_obj1) or (not is_int_obj2)):
            print ('obj1 or obj2 is NOT digit, cannot use ==/>< to compair')
            print obj1
            print obj2
            print_usage()
            sys.exit(1)
    elif (operator in ['.MATCH.', '.NOT_MATCH.', '.CONTAIN.', '.NOT_CONTAIN.']):
        if ((type(obj1) not in [type('str'), type(u'str'), type([])]) \
        or (type(obj2) not in [type('str'), type(u'str'), type([])])):
            print ('obj1 or obj2 is NOT string/list, cannot use MATCH/NOT_MATCH/CONTAIN/NOT_CONTAIN to compair')
            print obj1
            print obj2
            print_usage()
            sys.exit(1)
    elif (operator in ['.HAS_CHILDREN.', '.NOT_HAS_CHILDREN.']):
        if (type(obj1) != type({}) or type(obj2) != type('str')):
            print('path node is not a dict, can NOT use HAS_CHILDREN/NOT_HAS_CHILDREN operator')
            print obj1
            print obj2
            print_usage()
            sys.exit(1)
    else:
        print ('operator [%s] error' %(operator))
        print_usage()
        sys.exit(1)

    if (operator == '=='):
        if (int_obj1 == int_obj2):
            return True
        else:
            return False
    elif (operator == '!='):
        if (int_obj1 != int_obj2):
            return True
        else:
            return False
    elif (operator == '<='):
        if (int_obj1 <= int_obj2):
            return True
        else:
            return False
    elif (operator == '<'):
        if (int_obj1 < int_obj2):
            return True
        else:
            return False
    elif (operator == '>='):
        if (int_obj1 >= int_obj2):
            return True
        else:
            return False
    elif (operator == '>'):
        if (int_obj1 > int_obj2):
            return True
        else:
            return False
    elif (operator == '.MATCH.'):
        if (obj2 == ''):
            if (obj1 == ''):
                return True
            else:
                return False

        if (re.match(obj2, obj1) != None):
            return True
        else:
            return False
    elif (operator == '.NOT_MATCH.'):
        if (obj2 == ''):
            if (obj1 != ''):
                return True
            else:
                return False

        if (re.match(obj2, obj1) == None):
            return True
        else:
            return False
    elif (operator == '.CONTAIN.'):
        if (obj2 == ''):
            if (obj1 == ''):
                return True
            else:
                return False

        if (type(obj1) in [type('str'), type(u'str')]):
            obj2_ext = '.*'+obj2+'.*'
            if (re.match(obj2_ext, obj1) != None):
                return True
            else:
                return False
        elif (type(obj1) == type([])):
            if obj2 in obj1:
                return True
            else:
                return False
        else:
            print('unknown type of obj')
            sys.exit(1)
    elif (operator == '.NOT_CONTAIN.'):
        if (obj2 == ''):
            if (obj1 != ''):
                return True
            else:
                return False

        if (type(obj1) in [type('str'), type(u'str')]):
            obj2_ext = '.*'+obj2+'.*'
            if (re.match(obj2_ext, obj1) == None):
                return True
            else:
                return False
        elif (type(obj1) == type([])):
            if obj2 not in obj1:
                return True
            else:
                return False
        else:
            print('unknown type of obj')
            sys.exit(1)
    elif (operator == '.HAS_CHILDREN.'):
        for key in obj1.keys():
            if (re.match(obj2, key) != None):
                return True
            else:
                continue

        return False
    elif (operator == '.NOT_HAS_CHILDREN.'):
        for key in obj1.keys():
            if (re.match(obj2, key) != None):
                return False
            else:
                continue

        return True

def analyse_one_expr(one_expr, json_obj, cur_result, cur_level = 0, \
err_trace = {}, err_trace_parent = {}, err_trace_parent_key = '', err_trace_root = {}):
    path_node_list = one_expr['path_node_list']
    total_need_check_level = len(path_node_list)
    value = one_expr['value']
    operator = one_expr['operator']

    if (cur_level == 0):
        err_trace = {}
        err_trace_root = err_trace

    if (cur_level >= total_need_check_level):
        return 

    if (type(json_obj) != type({})):
        sys.stderr.write('---START error node found in original json START---\n')
        err_trace_parent[err_trace_parent_key] = json_obj
        sys.stderr.write(json.dumps(err_trace_root, indent = 4))
        sys.stderr.write('\n---END error node found in original json END---\n\n')
        return
    
    for key in json_obj.keys():
        if (re.match(path_node_list[cur_level], key) == None):
            continue

        # used to trace error json path
        err_trace.clear()
        err_trace[key] = {}

        if (not cur_result.has_key(key)):
            cur_result[key] = {}
        if (cur_level == total_need_check_level - 1):
            if (compair(json_obj[key], value, operator)):
                cur_result[key] = {'COMPAIR_STATE':'MATCH', 'VALUE':json_obj[key]}
            else:
                cur_result[key] = {'COMPAIR_STATE':'NOT FOUND OR NOT MATCH', 'VALUE':json_obj[key]}

            err_trace[key] = json_obj[key]
        else:
            analyse_one_expr(one_expr, json_obj[key], cur_result[key], cur_level + 1, \
            err_trace[key], err_trace, key, err_trace_root)

def merge_one_result(result, result_invert, sub_result, merge_method):
    for key in sub_result.keys():
        if (not result.has_key(key)):
            result[key] = {}
        if (not result_invert.has_key(key)):
            result_invert[key] = {}

        if (sub_result[key].keys() == ['COMPAIR_STATE', 'VALUE']):
            if (sub_result[key]['COMPAIR_STATE'] == 'MATCH'):
                # result[key]不为空,说明曾经出现过
                # 处理两个条件同时针对同一个节点的情况
                if (result[key] != {}):
                    # 如果原来是不match,但条件是and的情况
                    if ((result[key] == '!MATCH_FAILED!') and (merge_method == 'and')):
                        do_nothing()
                    # 如果原来是match,同时条件是and的情况
                    elif ((result[key] != '!MATCH_FAILED!') and (merge_method == 'and')):
                        do_nothing()
                    # 如果原来是不match,但条件是or的情况
                    elif ((result[key] == '!MATCH_FAILED!') and (merge_method == 'or')):
                        result[key] = sub_result[key]['VALUE']
                        result_invert[key] = '!INVERT_MATCH_FAILED!'
                    # 如果原来是match,同时条件是or的情况
                    elif ((result[key] != '!MATCH_FAILED!') and (merge_method == 'or')):
                        do_nothing()
                else:
                    result[key] = sub_result[key]['VALUE']
                    result_invert[key] = '!INVERT_MATCH_FAILED!'
            elif (sub_result[key]['COMPAIR_STATE'] == 'NOT FOUND OR NOT MATCH'):
                # result[key]不为空,说明曾经出现过
                # 处理两个条件同时针对同一个节点的情况
                if (result[key] != {}):
                    # 如果原来是不match,但条件是and的情况
                    if ((result[key] == '!MATCH_FAILED!') and (merge_method == 'and')):
                        do_nothing()
                    # 如果原来是match,同时条件是and的情况
                    elif ((result[key] != '!MATCH_FAILED!') and (merge_method == 'and')):
                        result[key] = '!MATCH_FAILED!'
                        result_invert[key] = sub_result[key]['VALUE']
                    # 如果原来是不match,但条件是or的情况
                    elif ((result[key] == '!MATCH_FAILED!') and (merge_method == 'or')):
                        do_nothing()
                    # 如果原来是match,同时条件是or的情况
                    elif ((result[key] != '!MATCH_FAILED!') and (merge_method == 'or')):
                        do_nothing()
                else:
                    result[key] = '!MATCH_FAILED!'
                    result_invert[key] = sub_result[key]['VALUE']
            else:
                print ('sub_result[%s][COMPAIR_STATE]=[%s] error' %(key, sub_result[key]['COMPAIR_STATE']))
                print_usage()
                sys.exit(1)

            result['!CHECK_BARRIER!'] = '!CHECK_POINT!'
            result_invert['!CHECK_BARRIER!'] = '!CHECK_POINT!'
        else:
            merge_one_result(result[key], result_invert[key], sub_result[key], merge_method)

def do_nothing():
    return

def clean_result(result, raw_result, raw_result_invert, merge_method, \
parent_raw_result = {}, parent_raw_result_invert= {}, parent_result = {}, parent_key = ''):
    if (type(raw_result) != type({})):
        return

    # 若父节点是需要校验的节点,则本节点也需要校验
    if (parent_raw_result.has_key('!CHECK_BARRIER!')):
        raw_result['!CHECK_BARRIER!'] = '!CHECK_POINT!'

    if (raw_result.has_key('!CHECK_BARRIER!')):
        if (merge_method == 'analyse_keys'):
            # 目前先只支持同时只分析同一层上的key,暂不支持多层
            for key in raw_result.keys():
                if (raw_result[key] != '!CHECK_POINT!'):
                    if (raw_result[key] != '!MATCH_FAILED!'):
                        result[key] = raw_result[key]
        else:
            has_matched_node = False
            has_not_matched_node = False
            # 先遍历完所有的子结果项
            for key in raw_result.keys():
                if (type(raw_result[key]) == type({})):
                    if (not result.has_key(key)):
                        result[key] = {}
                    clean_result(result[key], raw_result[key], raw_result_invert[key], merge_method, raw_result, raw_result_invert, result, key)

            # 必须单独再循环一遍,因为需要先遍历完所有的子结果项,以便子结果项的结果能够回馈上来
            for key in raw_result.keys():
                if (raw_result[key] != '!CHECK_POINT!'):
                    if (raw_result[key] != '!MATCH_FAILED!'):
                        has_matched_node = True
                    else:
                        has_not_matched_node = True

            tmp_result_node = {}
            # all match
            if (has_matched_node and (not has_not_matched_node)):
                # is highest level of checkpoint
                if (not parent_raw_result.has_key('!CHECK_BARRIER!')):
                    for key in raw_result.keys():
                        if (raw_result[key] != '!CHECK_POINT!'):
                            tmp_result_node[key] = raw_result[key]
                    result.update(tmp_result_node)
                # is not highest level of checkpoint
                else:
                    for key in raw_result.keys():
                        if (raw_result[key] == '!CHECK_POINT!'):
                            del raw_result[key]
            # match some
            elif (has_matched_node and has_not_matched_node):
                # is highest level of checkpoint
                if (not parent_raw_result.has_key('!CHECK_BARRIER!')):
                    if (merge_method == 'or'):
                        for key in raw_result.keys():
                            if (raw_result[key] != '!CHECK_POINT!'):
                                if (raw_result[key] != '!MATCH_FAILED!'):
                                    tmp_result_node[key] = raw_result[key]
                                else:
                                    tmp_result_node[key] = raw_result_invert[key]
                        result.update(tmp_result_node)
                    elif (merge_method == 'and'):
                        do_nothing()
                # is not highest level of checkpoint
                else:
                    if (merge_method == 'or'):
                        for key in raw_result.keys():
                            if (raw_result[key] == '!CHECK_POINT!'):
                                del raw_result[key]
                    elif (merge_method == 'and'):
                        parent_raw_result_invert[parent_key] = parent_raw_result[parent_key]
                        parent_raw_result[parent_key] = '!MATCH_FAILED!'
            # all not match
            elif ((not has_matched_node) and has_not_matched_node):
                if (parent_raw_result.has_key('!CHECK_BARRIER!')):
                    parent_raw_result_invert[parent_key] = parent_raw_result[parent_key]
                    parent_raw_result[parent_key] = '!MATCH_FAILED!'
                else:
                    do_nothing()
            else:
                print('impossible')
                print_usage()
                sys.exit(1)

    else:
        for key in raw_result.keys():
            if (not result.has_key(key)):
                result[key] = {}
            clean_result(result[key], raw_result[key], raw_result_invert[key], merge_method, raw_result, raw_result_invert, result, key)
    
    if (parent_result != {} and parent_key != '' and result == {}):
        del parent_result[parent_key]

def merge_final_result(result, result_invert, sub_result_list, merge_method):
    raw_result = {}
    raw_result_invert = {}
    for sub_result in sub_result_list:
        merge_one_result(raw_result, raw_result_invert, sub_result, merge_method)

    clean_result(result, raw_result, raw_result_invert, merge_method)
    #clean_result_invert(result_invert, raw_result, raw_result_invert, merge_method)

def analyse_json(json_obj, method, expr):
    sub_expr_kvs = parse_expr(expr)

    analyse_result_for_each_sub_expr = []
    for sub_kv in sub_expr_kvs:
        analyse_result_for_each_sub_expr.append({})
        cur_result = analyse_result_for_each_sub_expr[len(analyse_result_for_each_sub_expr) - 1]
        analyse_one_expr(sub_kv, json_obj, cur_result)

    final_result = {}
    final_result_invert = {}
    merge_final_result(final_result, final_result_invert, analyse_result_for_each_sub_expr, method)

    return (final_result, final_result_invert)
# analyse_json end

# main process begin
def main(argv):
    try:
        short_param = 'hi:m:e:'
        long_param = ['help', 'input=', 'method=', 'expr=']
        opts, args = getopt.getopt(argv[1:], short_param, long_param)
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    input_mode = 'stdin_mode'
    method = 'and'
    expr = ''
    output_mode = 'value'

    for o, v in opts:
        if o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        elif o in ('-i', '--input'):
            input_mode = 'file_mode'
            json_file_name = v
        elif o in ('-m', '--method'):
            method = v
        elif o in ('-e', '--expr'):
            expr = v
        else:
            print 'unknown option'
            print_usage()
            sys.exit(1)

    if (method not in ['and', 'or', 'analyse_keys']):
        print_usage()
        sys.exit(1)

    if (expr == ''):
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

    (result, result_invert) = analyse_json(json_obj, method, expr)
    if (output_mode == 'value'):
        print json.dumps(result, indent = 4)
    else:
        print ('output_mode=[%s] error' %(output_mode))
        print_usage()
        sys.exit(1)
    

if __name__ == '__main__':
    main(sys.argv)

