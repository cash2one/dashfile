#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
models=['bs','bc','attr','basa','dictserver','disp']
types=['dfail','freeze','new','null','repa','stop','unav','unknown']
for cluster in clusters:
    for type in types:
        infile="/home/work/data_if/"+cluster+"/"+type+".list"
        fin_list=open(infile).readlines()
        for model in models:
            outfile="/home/work/data_if/"+cluster+"/"+type+"_"+model+".list"
            fout=open(outfile,'w')  
            for x in fin_list:
                aa = x.split('\t')
                if model==aa[1]:
                    fout.write(x)        




