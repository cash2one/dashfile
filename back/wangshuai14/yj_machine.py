#!/usr/bin/python
#vim: set fileencoding=gb2312

import sys
stat_time=sys.argv[1]
clusters=['beijing','hangzhou','nanjing','shanghai','tucheng']
outfile="/home/work/data_if/machine.table.sql"
fout=open(outfile,'w')
format="\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d"
for cluster in clusters:
    str=''
    d1={}
    d2={}
    t=()
    infile1=open('/home/work/data/'+stat_time+'/'+cluster+'.machine_err.list')
    infile2=open('/home/work/data/'+stat_time+'/'+cluster+'.machine_health.list')
    for line1 in infile1.readlines():
        m=line1.strip().split('\t')
        n=m[1]
        x=d1.get(n,0)+1
        d1[n]=x
        if m[1]=='not_found':
            str+=m[0]+','
    for line2 in infile2.readlines():
        i=line2.strip().split('\t')
        j=i[2]
        h=d2.get(j,0)+1
        d2[j]=h
    t=(stat_time,cluster,str,d2.get('fix_mac',0),d2.get('handling',0),d1.get('not_found',0),d2.get('all_ok',0),d2.get('fix_ser',0),d2.get('handling_onser',0),d2.get('lv2cetus',0),d2.get('some_ser_err',0))
    print >>fout,format % t
