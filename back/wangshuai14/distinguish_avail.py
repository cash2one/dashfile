#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
for cluster in clusters:
    infile_instance="/home/work/data/latest/"+cluster+".instance.list"
    infile_agent="/home/work/data/latest/"+cluster+".agent.list"
    outfile_avail="/home/work/data_if/"+cluster+"/avail.list"
    outfile_unavail="/home/work/data_if/"+cluster+"/unav.list"

    fout_avail=open(outfile_avail,'w')
    fout_unavail=open(outfile_unavail,'w')
    li_instance=open(infile_instance).readlines()
    li_agent=open(infile_agent).readlines()

    dict={}
    for x in li_agent: 
        xx = x.split('\t')
        dict[xx[0]]=xx[2][0:-1]


    for x in li_instance:
        li_ins=x.split('\t')
        ip = li_ins[3]
        if ip in dict.keys():
            if dict[ip]=='avail':
                fout_avail.write(x)
            if dict[ip]=='unavail':
                fout_unavail.write(x)

