#!/usr/bin/python
import time
stat_time=time.strftime('%y%m%d_%H',time.localtime()) 
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
types=['dfail','freeze','new','null','repa','stop','unav','unknown']
models=['bs','bc','attr','basa','dictserver','disp']
outfile="/home/work/data_if/instance_fault.sql"
fout=open(outfile,'w')
format="\t%s\t%s\t%s\t%s\t%d"
for cluster in clusters:
    dict={}
    count=0
    t=()
    for type in types:
        for model in models:
            infile="/home/work/data_if/"+cluster+"/"+type+"_"+model+".list"
            fin_list=open(infile).readlines()
            count=len(fin_list)
            dict[type+"_"+model]=count
    #time,room,model,type,num
    for k,v in dict.items():
        k_list=k.split('_')
        t=(stat_time,cluster,k_list[1],k_list[0],v)
        print >> fout , format % t

