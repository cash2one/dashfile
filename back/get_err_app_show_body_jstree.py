#!/usr/bin/python

import sys
import json

def line2dict(all, i, number):

    if i == number:
        return all

    ret_dict = {}
    tmp_dict = {}
    for line in all:
        if "testenv" not in line:
            line = line.replace('\n', '')
            line = line.replace('PsWwwLog:9anachO9rongi!aRawol@szwg-rank-hdfs.dmop.baidu.com:54310/app/ps/searcher/frontend/beehive/deploy/bin_mirror/data/prod-64/ps/se', '...')
            data = line.split()[i];
            
            if data not in tmp_dict:
                tmp_dict[data] = []
            tmp_dict[data].append(line)
            #tmp_dict[data].append(line.split()[4])

    for k,v in tmp_dict.items():
        ret_dict[k] = line2dict(v, i + 1, number)

    return ret_dict

def dict2dictlen(d, i, number):
    if i == number:
        return d

    ret = {}
    for k1, v1 in d.items():
        le = getlen(v1, i + 1, number)
        k2 = (k1, le)
        v2 = dict2dictlen(v1, i + 1, number)
        ret[k2] = v2
    
    return ret

def dictlen2listlensort(d, i, number):
    if i == number:
        return d

    ll = []
    for k1, v1 in d.items():
        v2 = dictlen2listlensort(v1, i + 1, number)
        ll.append((k1, v2))
    ll.sort()

    return ll

def getlen(x, i, number):
    if i == number:
        return len(x)

    le = 0
    for k, v in x.items():
        this = getlen(v, i + 1, number)
        le += this
    return le

def func_sort(a, b):
    aa = a[0][0]
    bb = b[0][0]
    return bb - aa

index = 0

def print_better2(x, i, number, err_list):
    if i == number:
        retlist = []
        for line in x:
            columes = line.split()
            data_source = columes[1]
            instance_id = columes[4]
            ip = columes[5]
            d = {}
            d["id"] = instance_id + " " + ip
            d["text"] = instance_id + " " + ip
            d["icon"] = "glyphicon glyphicon-file"
            retlist.append(d)
        return retlist

    ret = []
    for k in x:
        children = print_better2(k[1], i + 1, number, err_list)

        global index
        m = {}
        m["id"] = index
        m["text"] = "%s(%d)" % (k[0][0], k[0][1])
        if i == 1:
            if k[0][0] in err_list:
                m["icon"] = "glyphicon glyphicon-remove"
            else:
                m["icon"] = "glyphicon glyphicon-ok"
        else:
            m["icon"] = "glyphicon glyphicon-folder-close"

        if len(children) > 0:
            m["children"] = children
        index += 1
        ret.append(m)
    return ret


def main():
    fi = sys.argv[1]
    fi_err = sys.argv[2]
    file_object = open(fi)
    file_object_err = open(fi_err)

    all_list = file_object.readlines()
    err_list = file_object_err.readlines()
    
    removeline = []
    for line in err_list:
        line = line.replace('\n', '')
        removeline.append(line)
        
    x = line2dict(all_list, 0, 4)
    y = dict2dictlen(x, 0, 4)
    z = dictlen2listlensort(y, 0, 4)
    print json.dumps(print_better2(z, 0, 4, removeline))

if __name__ == '__main__':
    main()
