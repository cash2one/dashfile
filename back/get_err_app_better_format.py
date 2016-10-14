#!/usr/bin/python

import sys

errlist = []

def line2dict(all, i, number):

    if i == number:
        return all

    ret_dict = {}
    tmp_dict = {}
    for line in all:
        if "testenv" not in line:
            line = line.replace('\n', '')
            data = line.split()[i];
            
            if data not in tmp_dict:
                tmp_dict[data] = []
            tmp_dict[data].append(line)

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

    if i == 0:
        for kk,vv in ret.items():
            if kk[1] < 500:
                errlist.append(kk[0])
    
    return ret

def dictlen2listlensort(d, i, number):
    if i == number:
        return d

    ll = []
    for k1, v1 in d.items():
        v2 = dictlen2listlensort(v1, i + 1, number)
        ll.append((k1, v2))
    ll.sort(func_sort)

    return ll

def make_li_min(d, i, number):
    if i == number:
        return

    print "<ul>",
    for k in d:
        print "<li>",
        print k[0][1], k[0][0],
        print "</li>",
        make_li_min(k[1], i + 1, number)
    print "</ul>",

def getlen(x, i, number):
    if i == number:
        return len(x)

    le = 0
    for k, v in x.items():
        this = getlen(v, i + 1, number)
        le += this
    return le

def func_sort(a, b):
    aa = a[0][1]
    bb = b[0][1]
    return bb - aa

def get_err_inst(all_list, elist):
    l = []
    for line in all_list:
        addr = line.split()[0]
        if addr in elist:
            l.append(line)
    return l

def get_err_app(all):
    appdict = {}
    for line in all:
        appid = line.split()[3]
        appdict[appid] = 0
    return appdict.keys()

def get_all_instance(all, e_app_list):
    retlist = []
    for line in all:
        appid = line.split()[3]
        if appid in e_app_list:
            retlist.append(line)
    return retlist

def better_format(all):
    for line in all:
        line = line.replace('\n', '')
        l = line.split()
        addr = l[0]
        ava = l[1]
        state = l[2]
        appid = l[3]
        instid = l[4]
        ip = l[5]
        print appid, addr, ava, state, instid, ip
    retlist = []

def main():
    fi = sys.argv[1]
    file_object = open(fi)
    all_list = file_object.readlines()
    x = line2dict(all_list, 0, 3)
    y = dict2dictlen(x, 0, 3)
    z = get_err_inst(all_list, errlist)
    err_app_list = get_err_app(z)
    all_err = get_all_instance(all_list, err_app_list)
    better_format(all_err)

if __name__ == '__main__':
    main()
