#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
for cluster in clusters:
    infile_instance="/home/work/data/latest/"+cluster+".instance.list"
    infile_naming="/home/work/data/latest/"+cluster+".naming.list"
    outfile_on_ns="/home/work/data_if/"+cluster+"/ns/on_ns.list"

    fout_on_ns=open(outfile_on_ns,'w')
    li_instance=open(infile_instance).readlines()
    li_naming=open(infile_naming).readlines()

    naming_list=[]
    for x in li_naming: 
        xx = x.split('\t')
        naming_list.append(xx[3][0:-1])

    for x in li_instance:
        li_ins=x.split('\t')
        id = li_ins[0]
        if id in naming_list:
            fout_on_ns.write(x)
