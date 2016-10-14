#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
types=['dfail','freeze','new','null','repa','stop','unav','unknown']
models=['bs','bc','attr','basa','dictserver','disp']
for cluster in clusters:
    for model in models:
        outfile="/home/work/data_if/"+cluster+"/total_"+model+".list"
        fout=open(outfile,'w')
        for type in types:
            infile="/home/work/data_if/"+cluster+"/"+type+"_"+model+".list"
            fin=open(infile).readlines()
            for x in fin:
                fout.write(x)

