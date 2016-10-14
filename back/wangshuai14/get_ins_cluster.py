#!/usr/bin/python

infile_hz="/home/work/data/latest/hangzhou.instance.list"
infile_nj="/home/work/data/latest/nanjing.instance.list"
infile_sh="/home/work/data/latest/shanghai.instance.list"
infile_tc="/home/work/data/latest/tucheng.instance.list"
infile_bj="/home/work/data/latest/beijing.instance.list"
outfile="/home/work/data_search/result_ins_cluster.txt"
fin_hz=open(infile_hz)
fin_nj=open(infile_nj)
fin_sh=open(infile_sh)
fin_tc=open(infile_tc)
fin_bj=open(infile_bj)
fout=open(outfile,'w')
map={}
for x in fin_hz.readlines():
    ins_id=x.split('\t')[0]
    map[ins_id]=['hangzhou']
for x in fin_nj.readlines():
    ins_id=x.split('\t')[0]
    if ins_id not in map:
        map[ins_id]=['nanjing']
    else:
        map[ins_id].append('nanjing')
for x in fin_sh.readlines():
    ins_id=x.split('\t')[0]
    if ins_id not in map:
        map[ins_id]=['shanghai']
    else:
        map[ins_id].append('shanghai')
for x in fin_tc.readlines():
    ins_id=x.split('\t')[0]
    if ins_id not in map:
        map[ins_id]=['tucheng']
    else:
        map[ins_id].append('tucheng')
for x in fin_bj.readlines():
    ins_id=x.split('\t')[0]
    if ins_id not in map:
        map[ins_id]=['beijing']
    else:
        map[ins_id].append('beijing')
print >> fout, map



    
    
