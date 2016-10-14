from django.http import HttpResponse
from django.shortcuts import render_to_response
import uniform
import time
def index(request):
    param_index=request.GET
    if len(param_index)==3:
        cluster = param_index['room']
        type=param_index['type']
        modeln=param_index['modeln']
        if modeln=='bs_on_ns':
            infile='/home/work/data_if/'+cluster+'/ns/'+type+'.list'
        else:
            infile='/home/work/data_if/'+cluster+'/'+type+'_'+modeln+'.list'
    else:
        cluster = param_index['cluster']
        model=param_index['model']
        if model=='bs_on_ns':
            infile='/home/work/data_if/'+cluster+'/ns/total.list'
        else:
            infile='/home/work/data_if/'+cluster+'/total_'+model+'.list'
    fin=open(infile)
    li = fin.readlines()
    result = []
    for x in li:
        data = x.strip('\n').split()
        ins_href = "<a href='http://dashboard.beehive.baidu.com:8888/show_instance?search=%s&cluster=%s' target='__blank'>%s</a>" % \
                  (data[0],cluster,data[0])
        mac_href = "<a href='http://dashboard.beehive.baidu.com:8888/show_instance?search=%s&cluster=%s' target='__blank'>%s</a>" % \
                  (data[3],cluster,data[3])
        data.extend([ins_href,mac_href])
        result.append(data)
    start = time.strftime('%Y-%m-%d',time.localtime(time.time()-24*3600*2))
    end = time.strftime('%Y-%m-%d',time.localtime())
    info = {'result':result,'cluster':cluster,'start':start,'end':end}
    return render_to_response('instance_list.html',info)
    

