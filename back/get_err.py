#!/usr/bin/python

import sys

def get_err_list(all):
    retlist = []
    d = {}

    for line in all:
        if "testenv" not in line:
            line = line.replace('\n', '')
            line = line.replace('PsWwwLog:9anachO9rongi!aRawol@szwg-rank-hdfs.dmop.baidu.com:54310/app/ps/searcher/frontend/beehive/deploy/bin_mirror/data/prod-64/ps/se', '...')
            data_source = line.split()[0];
            
            if data_source not in d:
                d[data_source] = 0
            d[data_source] += 1

    for k,v in d.items():
        if v < 500:
            print k

def main():
    fi = sys.argv[1]
    file_object = open(fi)
    all_list = file_object.readlines()
    get_err_list(all_list)

if __name__ == '__main__':
    main()
