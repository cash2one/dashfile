#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
types=['dfail','freeze','new','null','repa','stop','unav','unknown']
for cluster in clusters:
    outfile="/home/work/data_if/"+cluster+"/ns/total.list"
    fout=open(outfile,'w')
    for type in types:
        infile="/home/work/data_if/"+cluster+"/ns/"+type+".list"
        fin=open(infile).readlines()
        for x in fin:
            fout.write(x)

