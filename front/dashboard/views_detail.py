# -*- coding: cp936 -*-
from django.shortcuts import render_to_response
from dashboard.models import KpiInstance
from dashboard.models import KpiMachine
import get_detail
import uniform
import time
import get
import os

def show(request, room):
    dl = get_detail.getinfo_detail(request,room)
    which_items_list = which1_items_list = which2_items_list  = [['rate',u'比率'],['num',u'数量']]
    daylist = get_detail.daylist()
    weeklist = get_detail.weeklist()
    monthlist = get_detail.monthlist()
    #chart_machine_list
    chart_machine = uniform.mrate_better()
    chart_machine_list = chart_machine.items()
    chart_machine_list.sort(get.mcsort) 
    #machine_label_list
    machine_label = dl[10]
    #chart_instance_list    
    chart_instance_list = uniform.module()
    #chart_agent_list
    chart_agent_list = uniform.agent()
    # yj_time
    for x in dl[0]:
        x.stat = x.stat_time[2:4]+'.'+x.stat_time[4:6]+' '+x.stat_time[-2:]+':00'
    strtime = time.strftime('%Y-%m-%d',time.localtime())
    #consistency_time
    ptl = strtime.split('-')
    package_time = ltr_time = base_time = ptl[0][-2:]+ptl[1]+ptl[2]
    #consistency_header
    consistency_header = {}
    for x in uniform.cluster():
        consistency_header[x] = []
    for cc in consistency_header.keys():
        bo = lo = do = ''
        path_base = "/home/work/data_zk_consistent/"+base_time+"/"+cc+"_base_bs_header"
        if os.path.exists(path_base):
            base_open = open(path_base)
            bo = base_open.read()   
        path_ltr = "/home/work/data_zk_consistent/"+ltr_time+"/"+cc+"_ltr_ranksvm_model_chn_header"
        if os.path.exists(path_ltr):
            ltr_open = open(path_ltr)
            lo = ltr_open.read()
        path_date = "/home/work/data_zk_consistent/"+package_time+"/"+cc+"_package_date_source_header"
        if os.path.exists(path_date):
            date_open = open(path_date)
            do = date_open.read() 
        consistency_header[cc].extend([do,lo,bo]) 
    consistency = [ ['package_date_source',package_time],['ltr_ranksvm_model_chn',ltr_time],['base_bs',base_time] ] 
    # kpi_machine
    km = list(KpiMachine.objects.filter(cluster=room).order_by("-stat_time")[0:15])
    km.reverse()
    for x in km:
        x.stat_time = x.stat_time[4:6]
    # kpi_instance
    ki = list(KpiInstance.objects.filter(cluster=room).order_by("-stat_time")[0:15])
    ki.reverse()      
    #unused machine
    um_date = strtime
    unused_machine = {}
    l = uniform.cluster_short()
    for x in l:
        unused_machine[x] = ''
    for cluster in l:
        infile = "/home/work/data_unused_machine/"+um_date+"/02-00/"+cluster+".analyse_machine_userate.result"
        umstr = ''
        if os.path.exists(infile):
            fin = open(infile).readlines()
            for x in fin[3:]:
                x = x.replace('\n','</br>')
                x = x.replace(' ', '&nbsp;')
                x = x.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
                if '(' in x and ')' in x :
                    start = x.index('file:&nbsp;')
                    end = x.index(')')
                    substr = x[start:end]
                    x = x.replace(substr,"<a href='/um_open?file="+substr+"' target='_blank'>list</a>")
                umstr += x
        unused_machine[cluster] = umstr
    #date_list
    mia_date_list = monthlist+weeklist+daylist
    #info 
    info = {"room":room,'city':uniform.cluster(),'which_items_list':which_items_list,'yj_table':dl[0],
    'qsm':dl[1],'qsi':dl[2],'chart_machine_list':chart_machine_list,'chart_instance_list':chart_instance_list,
    'which1_items_list':which1_items_list,'time_mac':dl[3],'time_ins':dl[4],'tuple_day_mac':dl[5],'tuple_day_ins':dl[6],
    'daylist':daylist,'weeklist':weeklist,'monthlist':monthlist,'qsa':dl[7],'time_agent':dl[8],'tuple_day_agent':dl[9],
    'chart_agent_list':chart_agent_list,'which2_items_list':which2_items_list,'consistency_header':consistency_header,
    'consistency':consistency,'km':km,'ki':ki,'unused_machine':unused_machine,'cd_package':strtime,'cd_ltr':strtime,'cd_base':strtime,
    'um_date':um_date,'machine_label':machine_label,'mia_date_list':mia_date_list
    }
    return render_to_response('detail.html',info)
