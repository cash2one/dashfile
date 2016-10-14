# -*- coding: cp936 -*-
from django.shortcuts import render_to_response
from dashboard.models import InstanceFaultNs
import get
import uniform

def index(request):
    list_str = get.getdata(request)
    l = uniform.cluster()
    mi_count = {}
    for x in l:
        mi_count[x] = 0
    hours = 24 
    instance_fault = list(InstanceFaultNs.objects.order_by("-time", "room", "type")[0:40]) 
    instance_fault_old = list(InstanceFaultNs.objects.order_by("-time", "room", "type")[40*hours:40*hours+40]) 
    new_fault = {}
    new_fault_total = {}
    for x in l:
        new_fault_total[x] = {}
        new_fault_total[x]['total'] = 0
        new_fault_total[x]['total_delta'] = 0
    for i in instance_fault:
        if i.room not in new_fault.keys():
            new_fault[i.room] = []
        index = instance_fault.index(i)
        oldnum = instance_fault_old[index].num if len(instance_fault_old) > 0 else 0
        deltanum = i.num - oldnum
        new_fault[i.room].append({"room":i.room, "type":i.type, "num":i.num, "num_delta":deltanum})
        new_fault_total[i.room]["total"] += i.num
        new_fault_total[i.room]["total_delta"] += deltanum
        if i.type == 'dfail':
            mi_count[i.room] = i.num
    new_fault_list = [[],[],[],[],[]]
    for x in l:
        id = l.index(x)
        new_fault_list[id] = new_fault[x]
    kpi_list = [['machine',u'机器 总使用率 平均'],['instance',u'core 实例存活率 95分位']]
    chart_machine = {"all":u'总使用率', "online":u'标记online率', "hard":u'硬故障率', "soft":u'软故障率', "no_err":u'无故障率', "no_err_use":u'无故障使用率'}
    chart_machine_list = chart_machine.items()
    chart_machine_list.sort(get.mcsort)
    machine_where_list = instance_where_list = ['rate','num'] 
    machine_switch_list = instance_switch_list = ['on','off'] 
    chart_items_list = new_fault_items_list = uniform.module()
    new_fault_time = [[1,'1h'],[24,'1d']]
    #history
    history = get.get_history()
    for x in history:
        x[2] = x[2][2:4]+'/'+x[2][4:6]+' '+x[2][-2:]+':00'
    #kpi
    km = list_str['kpi_machine']
    kpi = []
    for i in range(0,5):
        kpi.append([km[i][0].cluster,km[i][0].stat_time,km[i][0].latest_24,km[i][0].day_30,km[i][0].latest_30])
    print get.get_core()                     
    infos = {'list_str':list_str,'chart_machine_list':chart_machine_list, 'chart_items_list':chart_items_list, 
             'core_info':get.get_core(),'history':history,'kpi':kpi,'new_fault_list':new_fault_list, 
             'mi_count':mi_count,'new_fault_items_list':new_fault_items_list,'new_fault_total':new_fault_total,
             'kpi_list':kpi_list,'machine_where_list':machine_where_list,'machine_switch_list':machine_switch_list,   
             'instance_where_list':instance_where_list,'instance_switch_list':instance_switch_list,'city':uniform.cluster(), 
             'zk_map':get.get_zk_info(),'new_fault_time':new_fault_time 
            }
    return render_to_response('index.html', infos)
