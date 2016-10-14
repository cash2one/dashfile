#!/usr/bin/python

import sys

button = '''
<button type="button" class="btn btn-default btn-xs" aria-label="Left Align">
    <a href="" target="_blank"><span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></a>
</button>
'''


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
    ll.sort(func_sort)

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
    aa = a[0][1]
    bb = b[0][1]
    return bb - aa

def print_better(x, i, number):
    if i == number:
        return

    print "<ul>"
    for k,v in x.items():
        print "<li>",
        print k, 
        print "</li>",
        print_better(v, i + 1, number)
    print "</ul>"

def main():
    fi = sys.argv[1]
    file_object = open(fi)
    all_list = file_object.readlines()
    x = line2dict(all_list, 0, 4)
    print_better(x, 0, 4)

if __name__ == '__main__':
    main()
