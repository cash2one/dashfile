#!/usr/bin/python
import time
localtime=time.localtime()
stat_time=time.strftime('%y%m%d_%H',localtime) 
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
types=['dfail','freeze','new','null','repa','stop','unav','unknown']
outfile="/home/work/data_if/instance_fault_ns.sql"
fout=open(outfile,'w')
format="\t%s\t%s\t%s\t%d"
for cluster in clusters:
    dict={}
    count=0
    t=()
    for type in types:
        infile="/home/work/data_if/"+cluster+"/ns/"+type+".list"
        fin_list=open(infile).readlines()
        count=len(fin_list)
        dict[type]=count
    #time,cluster,type,num
    for k,v in dict.items():
        t=(stat_time,cluster,k,v)
        print >> fout , format % t
   

