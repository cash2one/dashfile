#!/usr/bin/python
import time
localtime=time.localtime()
stat_time=time.strftime('%y%m%d_%H',localtime) 
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
outfile="/home/work/data_if/ns_total.sql"
fout=open(outfile,'w')
format="\t%s\t%s\t%d\t%d\t%.4f"
for cluster in clusters:
    infile="/home/work/data_if/"+cluster+"/ns/total.list"
    fin_list=open(infile).readlines()
    count=len(fin_list)
    infile_ns="/home/work/data_if/"+cluster+"/ns/on_ns.list"
    fin_list_ns=open(infile_ns).readlines()
    count_ns=len(fin_list_ns)
    #time,cluster,num
    t=(stat_time,cluster,count,count_ns,float(count)/count_ns)
    print >> fout , format % t
   

