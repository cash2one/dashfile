#!/usr/bin/python
clusters=['hangzhou','nanjing','shanghai','tucheng','beijing']
for cluster in clusters:
    infile_false="/home/work/data_if/"+cluster+"/ns/false.list"

    outfile_deployfail="/home/work/data_if/"+cluster+"/ns/dfail.list"
    outfile_new="/home/work/data_if/"+cluster+"/ns/new.list"
    outfile_null="/home/work/data_if/"+cluster+"/ns/null.list"
    outfile_repair="/home/work/data_if/"+cluster+"/ns/repa.list"
    outfile_running="/home/work/data_if/"+cluster+"/ns/running.list"
    outfile_stop="/home/work/data_if/"+cluster+"/ns/stop.list"
    outfile_unknown="/home/work/data_if/"+cluster+"/ns/unknown.list"

    fout_deployfail=open(outfile_deployfail,'w')
    fout_new=open(outfile_new,'w')
    fout_null=open(outfile_null,'w')
    fout_repair=open(outfile_repair,'w')
    fout_running=open(outfile_running,'w')
    fout_stop=open(outfile_stop,'w')
    fout_unknown=open(outfile_unknown,'w')

    li_false=open(infile_false).readlines()

    for x in li_false:
        if 'DEPLOYFAIL' in x:
            fout_deployfail.write(x)
        if 'NEW' in x:
            fout_new.write(x)
        if 'NULL' in x:
            fout_null.write(x)
        if 'REPAIR' in x:
            fout_repair.write(x)
        if 'RUNNING' in x:
            fout_running.write(x)
        if 'STOP' in x:
            fout_stop.write(x)
        if 'UNKNOWN' in x:
            fout_unknown.write(x)

