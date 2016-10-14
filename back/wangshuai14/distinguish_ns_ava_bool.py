#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
for cluster in clusters:
    infile_avail="/home/work/data_if/"+cluster+"/ns/avail.list"
    outfile_false="/home/work/data_if/"+cluster+"/ns/false.list"
    outfile_true="/home/work/data_if/"+cluster+"/ns/freeze.list"

    fout_false=open(outfile_false,'w')
    fout_true=open(outfile_true,'w')

    li_avail=open(infile_avail).readlines()

    for x in li_avail:
        if 'False' in x:
            fout_false.write(x)
        if 'True' in x:
            fout_true.write(x)

