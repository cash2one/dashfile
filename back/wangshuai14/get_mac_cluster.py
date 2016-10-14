#!/usr/bin/python

infile_hz="/home/work/data/latest/hangzhou.machine.list"
infile_nj="/home/work/data/latest/nanjing.machine.list"
infile_sh="/home/work/data/latest/shanghai.machine.list"
infile_tc="/home/work/data/latest/tucheng.machine.list"
infile_bj="/home/work/data/latest/beijing.machine.list"
outfile="/home/work/data_search/result_mac_cluster.txt"
fin_hz=open(infile_hz)
fin_nj=open(infile_nj)
fin_sh=open(infile_sh)
fin_tc=open(infile_tc)
fin_bj=open(infile_bj)
fout=open(outfile,'w')
map={}
for x in fin_hz.readlines():
    ip=x.strip().split('\t')[0]
    map[ip]='hangzhou'
for x in fin_nj.readlines():
    ip=x.strip().split('\t')[0]
    map[ip]='nanjing'
for x in fin_sh.readlines():
    ip=x.strip().split('\t')[0]
    map[ip]='shanghai'
for x in fin_tc.readlines():
    ip=x.strip().split('\t')[0]
    map[ip]='tucheng'
for x in fin_bj.readlines():
    ip=x.strip().split('\t')[0]
    map[ip]='beijing'
print >> fout, map



    
    
