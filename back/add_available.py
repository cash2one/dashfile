#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json
import time 

stat_time=time.strftime('%y%m%d',time.localtime())

def make_unavailable_list(room):
    file_object = open('/home/work/data/latest/%s.agent.list' % room)
    l = []

    for line in file_object:
        line = line.replace('\n', '')
        listx = line.split('\t')
        if listx[2] == "unavail":
            l.append(listx[0])
    return l

def make_data(unavalist, name, foutx): 
    file_object = open(name)
    for line in file_object:
        list_in_line = line.split();
        appid = list_in_line[0]
        instid = list_in_line[1]
        status = list_in_line[2]
        ip = list_in_line[3]
        data = list_in_line[4]
        ava = 'UNAVA' if ip in unavalist else 'AVA'
        print >> foutx, "%s %s %s %s %s %s" % (data,ava,status,appid,instid,ip)

def main():
    cluster = sys.argv[1]

    infile1 = "./package_date_source.tmp"
    infile2 = "./ltr_ranksvm_model_chn.tmp"
    infile3 = "./base_bs.tmp"

    outfile1 = "/home/work/data_zk_consistent/"+stat_time+"/%s_package_date_source" % cluster
    outfile2 = "/home/work/data_zk_consistent/"+stat_time+"/%s_ltr_ranksvm_model_chn" % cluster
    outfile3 = "/home/work/data_zk_consistent/"+stat_time+"/%s_base_bs" % cluster

    fout1 = open(outfile1, 'w')
    fout2 = open(outfile2, 'w')
    fout3 = open(outfile3, 'w')

    unavalist = make_unavailable_list(cluster)
    make_data(unavalist, infile1, fout1)
    make_data(unavalist, infile2, fout2)
    make_data(unavalist, infile3, fout3)

if __name__ == '__main__':
    main()
