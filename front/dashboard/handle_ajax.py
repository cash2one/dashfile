from django.http import HttpResponse
from django.http import JsonResponse
from django.core.cache import cache
from dashboard.models import KpiInstance
from dashboard.models import KpiMachine
from dashboard.models import StatMachine
from dashboard.models import StatInstance
from dashboard.models import InstanceFault
from dashboard.models import InstanceFaultNs
from dashboard.models import StatAgent
from dashboard.models import StatMachineNew
from dashboard.models import NsTotal
from dashboard.models import InsHistory
import uniform
import json
import os
import datetime
import time

def ajax_instance(request):
    infile = "/home/work/data_search/result_ins_cluster.txt"
    fin = open(infile)
    search_txt = request.GET.get('search_txt','0')
    search_list = []
    if search_txt != '0':
        if not cache.has_key('cluster_map'):
            cluster_map = eval(fin.read())
            cache.set('cluster_map',cluster_map,None)
        dict = cache.get('cluster_map')
        search_list = dict.get(search_txt,'none')
    return JsonResponse(search_list,safe=False)

def ajax_machine(request):
    infile = "/home/work/data_search/result_mac_cluster.txt"
    fin = open(infile)
    search_txt = request.GET.get('search_txt','0')
    result = ""
    if search_txt != '0':
        if not cache.has_key('machine_map'):
            machine_map = eval(fin.read())
            cache.set('machine_map',machine_map,None)
        dict = cache.get('machine_map')
        result = dict.get(search_txt,'none')
    return HttpResponse(result)

def ajax_kpi(request):
    km = []
    sym = request.GET.get('kpi','default')
    for jifang in uniform.cluster():
        if sym == 'machine': 
            kpi_element = list(KpiMachine.objects.filter(cluster=jifang).order_by("-stat_time")[0:1])
            kpi_element[0].latest_24 = str("%.2f"%kpi_element[0].latest_24)
            kpi_element[0].day_30 = str("%.2f"%kpi_element[0].day_30)
            kpi_element[0].latest_30 = str("%.2f"%kpi_element[0].latest_30)
        else:
            kpi_element = list(KpiInstance.objects.filter(cluster=jifang).order_by("-stat_time")[0:1])
            kpi_element[0].per_24 = str("%.2f"%kpi_element[0].per_24)
            kpi_element[0].per_day_30 = str("%.2f"%kpi_element[0].per_day_30)
            kpi_element[0].per_latest_30 = str("%.2f"%kpi_element[0].per_latest_30)
        km.append(kpi_element)
    kpi = {}    
    cl = uniform.cluster()
    if sym == 'machine':
        for x in cl:
            id = cl.index(x)
            kpi[x] = [km[id][0].latest_24,km[id][0].day_30,km[id][0].latest_30]
    else:
        for x in cl:
            id = cl.index(x)
            kpi[x] = [km[id][0].per_24,km[id][0].per_day_30,km[id][0].per_latest_30]
    return JsonResponse(kpi)

def ajax_index_machine(request):  
    param = request.GET 
    r = param.get('machine')
    where0 = param.get('where0')
    switch = param.get('switch')
    map = {}
    for x in uniform.cluster():
        map[x] = []
    l = uniform.cluster()
    for jifang in l:
        machine_today = list(reversed(list(StatMachine.objects.filter(cluster=jifang,label='*all*').order_by("-stat_time")[0:24])))
        machine_yes = list(reversed(list(StatMachine.objects.filter(cluster=jifang,label='*all*').order_by("-stat_time")[24:48])))
        mt = []
        for x in machine_today:
            rate_map = {'all':x.running_rate,'no_err_use':x.no_err_running_rate,'hard':x.hard_err_rate,'no_err':x.no_err_rate,\
                        'online':x.online_rate,'soft':x.soft_err_rate}
            rate = rate_map[r] 
            if where0 == 'rate':
                mt.append(rate)
            else:
                mt.append(int(round(x.all_machine*rate/100)))
        my = []
        for x in machine_yes:
            rate_map = {'all':x.running_rate,'no_err_use':x.no_err_running_rate,'hard':x.hard_err_rate,'no_err':x.no_err_rate,\
                        'online':x.online_rate,'soft':x.soft_err_rate}
            rate = rate_map[r] 
            if where0 == 'rate':
                my.append(rate)
            else:
                my.append(int(round(x.all_machine*rate/100)))
        mac_time = []
        for t in machine_today:
           mac_time.append(t.stat_time[-2:])
        labelm = 'machine' + str(l.index(jifang) + 1)
        sym = '%' if where0 == 'rate' else ''
        machine = [labelm, mac_time, mt, my,sym]
        map[jifang] = machine
    if switch == 'on':
        today_list = yes_list = []
        for x in uniform.cluster():
            today_list += map[x][2]
            yes_list += map[x][3]
        max_today = max(today_list)       
        min_today = min(today_list)       
        max_yes = max(yes_list)       
        min_yes = min(yes_list) 
        mmax = max([max_today,max_yes])
        mmin = min([min_today,min_yes])
        map['mmax'] = mmax
        map['mmin'] = mmin
    return JsonResponse(map)

def ajax_index_instance(request):  
    param = request.GET 
    biaoqian = param.get('chart')
    where = param.get('where')
    switch1 = param.get('switch1')
    map = {}
    l = uniform.cluster()
    for x in l:
        map[x] = []
    for jifang in l:
        if biaoqian == "bs_on_ns":
            instance_today = list(reversed(list(NsTotal.objects.filter(room=jifang).order_by("-time")[0:24])))
            instance_yes = list(reversed(list(NsTotal.objects.filter(room=jifang).order_by("-time")[24:48])))
        else:
            instance_today = list(reversed(list(StatInstance.objects.filter(cluster=jifang,module=biaoqian).order_by("-stat_time")[0:24])))
            instance_yes = list(reversed(list(StatInstance.objects.filter(cluster=jifang,module=biaoqian).order_by("-stat_time")[24:48])))
        it = []
        if biaoqian == "bs_on_ns":
            for x in instance_today:
                if where == 'rate':
                    it.append(round(x.live_rate*100,2))
                else:
                    it.append(x.total)
        else:
            for x in instance_today:
                if where == 'rate':
                    it.append(round(100-x.live_rate,2))
                else:
                    it.append(int(round(x.all_instance*(100-x.live_rate)/100)))
        iy = []
        if biaoqian == "bs_on_ns":
            for x in instance_yes:
                if where == 'rate':
                    iy.append(round(x.live_rate*100,2))
                else:
                    iy.append(x.total)
        else:
            for x in instance_yes:
                if where == 'rate':
                    iy.append(round(100-x.live_rate,2))
                else:
                    iy.append(int(round(x.all_instance*(100-x.live_rate)/100)))
        ins_time = []
        if biaoqian == "bs_on_ns":
            for t in instance_today:
               ins_time.append(t.time[-2:])
        else:
            for t in instance_today:
               ins_time.append(t.stat_time[-2:])
        
        labeli = 'instance' + str(l.index(jifang) + 1)
        sym = '%' if where == 'rate' else ''
        instance = [labeli, ins_time, it, iy,sym]
        map[jifang] = instance
    if switch1 == 'on':
        today_list = yes_list = []
        for x in uniform.cluster():
            today_list += map[x][2]
            yes_list += map[x][3]
        max_today = max(today_list)       
        min_today = min(today_list)       
        max_yes = max(yes_list)       
        min_yes = min(yes_list) 
        mmax = max([max_today,max_yes])
        mmin = min([min_today,min_yes])
        map['mmax'] = mmax
        map['mmin'] = mmin
        map['kaiguan'] = True
    return JsonResponse(map)

def ajax_new_fault(request):
    param = request.GET
    l = uniform.cluster()
    mi_count = {}
    for x in l:
        mi_count[x] = 0
    modeln = param.get('new_fault')
    countn = param.get('new_fault_time')
    nhours = int(countn)
    fault_type = param.get('fault_type','nothing')
    if modeln == 'bs_on_ns':
        instance_fault = list(InstanceFaultNs.objects.order_by("-time", "room", "type")[0:40])
        instance_fault_old = list(InstanceFaultNs.objects.order_by("-time", "room", "type")[40*nhours:40*nhours+40])
    else:
        instance_fault = list(InstanceFault.objects.filter(model=modeln).order_by("-time", "room", "model", "type")[0:40])
        instance_fault_old = list(InstanceFault.objects.filter(model=modeln).order_by("-time", "room", "model", "type")[40*nhours:40*nhours+40])
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
        if i.type == fault_type:
            mi_count[i.room] = i.num
    new_fault_list = [[],[],[],[],[]]
    for x in l:
        id = l.index(x)
        new_fault_list[id] = new_fault[x]
    map = {'new_fault_list':new_fault_list,'new_fault_total':new_fault_total,'mi_count':mi_count}
    return JsonResponse(map)


def ajax_detail_package(request):
    param = request.GET
    cd_package = param.get('cd_package')
    ptl = cd_package.split('-')
    package_time = ptl[0][-2:]+ptl[1]+ptl[2]
    consistency_header = {}
    l = uniform.cluster()
    for x in l:
        consistency_header[x] = []
    for cc in l:
        path_date = "/home/work/data_zk_consistent/"+package_time+"/"+cc+"_package_date_source_header"
        do = ''
        if os.path.exists(path_date):
            date_open = open(path_date)
            do = date_open.read()
        consistency_header[cc].append(do)
    return JsonResponse(consistency_header);

def ajax_detail_ltr(request):
    param = request.GET
    cd_ltr = param.get('cd_ltr')
    ltl = cd_ltr.split('-')
    ltr_time = ltl[0][-2:]+ltl[1]+ltl[2]
    consistency_header = {}
    l = uniform.cluster()
    for x in l:
        consistency_header[x] = []
    for cc in l:
        path_ltr = "/home/work/data_zk_consistent/"+ltr_time+"/"+cc+"_ltr_ranksvm_model_chn_header"
        lo = ''
        if os.path.exists(path_ltr):
            ltr_open = open(path_ltr)
            lo = ltr_open.read()
        consistency_header[cc].append(lo)
    return JsonResponse(consistency_header);

def ajax_detail_base(request):
    param = request.GET
    cd_base = param.get('cd_base')
    btl = cd_base.split('-')
    base_time = btl[0][-2:]+btl[1]+btl[2]
    consistency_header = {}
    l = uniform.cluster()
    for x in l:
        consistency_header[x] = []
    for cc in l:
        path_base = "/home/work/data_zk_consistent/"+base_time+"/"+cc+"_base_bs_header"
        bo = ''
        if os.path.exists(path_base):
            base_open = open(path_base)
            bo = base_open.read()   
        consistency_header[cc].append(bo)
    return JsonResponse(consistency_header);

def ajax_detail_um(request):
    param = request.GET       
    um_date = param.get('um_date')
    l = uniform.cluster_short()
    unused_machine = {}
    for x in l:
        unused_machine[x] = ''
    for cluster in l:
        umstr = ''
        infile = "/home/work/data_unused_machine/"+um_date+"/02-00/"+cluster+".analyse_machine_userate.result"
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
                    x = x.replace(substr,"<a href='/um_open?file="+substr+"&um_date="+um_date+"' target='_blank'>list</a>")
                umstr += x
        unused_machine[cluster] = umstr
    return JsonResponse(unused_machine)

TT = 'day_'+time.strftime('%Y-%m-%d',time.localtime())

def mia_date(d_li):
    start = 0
    end = 24
    today = datetime.datetime.today()
    if d_li[0] == 'day':
        str2 = time.strptime(d_li[1],'%Y-%m-%d')
        str3 = datetime.datetime(str2[0],str2[1],str2[2])
        result = today-str3
        d_get = result.days
        day_x = today-datetime.timedelta(days=d_get+1)
        start = d_get*24
        end = start+24
    elif d_li[0] == 'week':
        str2 = time.strptime(d_li[1],'%Y-%m-%d')
        str3 = datetime.datetime(str2[0],str2[1],str2[2])
        result = today-str3
        d_get = result.days
        day_x = today-datetime.timedelta(days=d_get+7)
        start = d_get*24
        end = start+7*24
    elif d_li[0] == 'mon':
        str2 = time.strptime(d_li[1],'%Y-%m-%d')
        str3 = datetime.datetime(str2[0],str2[1],str2[2])
        result = today-str3
        d_get = result.days
        day_x = today-datetime.timedelta(days=d_get+30)
        start = d_get*24
        end = start+30*24
    elif d_li[0] == 'any':
        time1 = time.strptime(d_li[1],'%Y-%m-%d')
        date1 = datetime.datetime(time1[0],time1[1],time1[2])
        time2 = time.strptime(d_li[2],'%Y-%m-%d')
        date2 = datetime.datetime(time2[0],time2[1],time2[2])
        result = today-date1
        d_get = result.days
        day_x = today-datetime.timedelta(days=d_get)
        start1_tuple = today-date2
        end1_tuple = today-date1
        start = start1_tuple.days*24
        end = end1_tuple.days*24
    else:
        pass
    return [start,end,day_x]

def ajax_detail_machine(request,jifang):  
    param = request.GET
    global TT
    d = param.get('time',TT)
    y = param.get('which','rate')
    r = param.get('machine','all')
    label = param.get('label','*all*')
    d_li = d.split('_')
    res = mia_date(d_li)
    start = res[0]
    end = res[1]
    day_x = res[2]
    tuple_day_mac = [day_x.year,day_x.month-1,day_x.day,day_x.hour+8]
    qst_mac = list(StatMachineNew.objects.filter(cluster=jifang,label=label).order_by("-stat_time")[start:end])
    qst_mac.reverse()
    qsm = []
    rate = 0
    for x in qst_mac:
        rate_map = {'all':x.running_rate,'no_err_use':x.no_err_running_rate,'hard':x.hard_err_rate,'no_err':x.no_err_rate,\
                    'online':x.online_rate,'soft':x.soft_err_rate}
        rate = rate_map[r] 
        if y == 'rate':
            qsm.append(rate)
        else:
            qsm.append(int(round(x.all_machine*rate/100)))
    time_mac = []
    for t in qst_mac:
        time_mac.append(t.stat_time)
    sym = '' if y == 'num' else '%'
    map = {"qsm":qsm,"time_mac":time_mac,"tuple_day_mac":tuple_day_mac, "sym":sym}
    return JsonResponse(map)

def ajax_detail_instance(request,jifang):  
    param = request.GET
    biaoqian = param.get('instance','bs');
    global TT
    d1 = param.get('time1',TT)
    y1 = param.get('which1','rate')
    d_li = d1.split('_')
    res = mia_date(d_li)
    start = res[0]
    end = res[1]
    day_x = res[2]
    tuple_day_ins = [day_x.year,day_x.month-1,day_x.day,day_x.hour+8]
    if biaoqian == "bs_on_ns":
        qst_ins = list(NsTotal.objects.filter(room=jifang).order_by("-time")[start:end])
    else:
        qst_ins = list(StatInstance.objects.filter(cluster=jifang,module=biaoqian).order_by("-stat_time")[start:end])
    qst_ins.reverse()
    qsi = []
    if biaoqian == "bs_on_ns":
        for x in qst_ins:
            if y1 == 'rate':
                qsi.append(round(x.live_rate*100,2))
            else:
                qsi.append(int(x.on_ns*x.live_rate))
    else:
        for x in qst_ins:
            if y1 == 'rate':
                qsi.append(round(100-x.live_rate,2))
            else:
                qsi.append(int(round(x.all_instance*(100-x.live_rate)/100)))
    time_ins = []
    if biaoqian == "bs_on_ns":
        for t in qst_ins:
            time_ins.append(t.time)
    else:
        for t in qst_ins:
            time_ins.append(t.stat_time)
    sym = '' if y1 == 'num' else '%'
    map = {"qsi":qsi,"time_ins":time_ins,"tuple_day_ins":tuple_day_ins, "sym":sym}
    return JsonResponse(map)

def ajax_detail_agent(request,jifang):
    param = request.GET
    global TT  
    d2 = param.get('time2',TT)
    y2 = param.get('which2','rate')
    r1 = param.get('agent','all')
    d_li = d2.split('_')
    res = mia_date(d_li)
    start = res[0]
    end = res[1]
    day_x = res[2]
    tuple_day_agent = [day_x.year,day_x.month-1,day_x.day,day_x.hour+8]
    qst_agent = list(StatAgent.objects.filter(cluster=jifang).order_by("-stat_time")[start:end])
    qst_agent.reverse()
    qsa = []
    for x in qst_agent:
        if r1 == 'all':
            rate = x.all_avail_rate
            if y2 == 'rate':
                qsa.append(rate)
            else:
                qsa.append(int(round(x.all_machine*rate/100)))
        else :
            rate = x.no_hard_err_avail_rate
            if y2 == 'rate':
                qsa.append(rate)
            else:
                qsa.append(int(round(x.no_hard_err_machine*rate/100)))
    time_agent = []
    for t in qst_agent:
        time_agent.append(t.stat_time)
    sym = '' if y2 == 'num' else '%'
    map = {"qsa":qsa,"time_agent":time_agent,"tuple_day_agent":tuple_day_agent, "sym":sym}
    return JsonResponse(map)

def get_state_list(t,state_list):
    state = []
    for x in state_list:
        if x == t:
            state.append(1)
        else:
            state.append("")
    return state

def ajax_show_instance(request):
    param = request.GET
    curhour = time.localtime()[3]+8
    start_get = param.get('start')
    end_get = param.get('end')
    search = param.get('search')
    cluster = param.get('cluster')
    start = start_get+' '+str(curhour)+':00:00'
    sreal = time.strptime(start,'%Y-%m-%d %H:%M:%S')
    start_tuple = [sreal[0],sreal[1]-1,sreal[2],sreal[3]]
    end = end_get+' '+str(curhour)+':00:00'
    ereal = time.strptime(end,'%Y-%m-%d %H:%M:%S')
    ins_history = InsHistory.objects.filter(instance_id=search,cluster=cluster,timestamp__range=(start,end)\
                  ).values("state","timestamp")
    ss = time.mktime(sreal)
    ee = time.mktime(ereal)
    all_time = []
    for x in range(int(ss),int(ee)+1,3600):
        loc = time.localtime(x)
        locstr = time.strftime('%Y-%m-%d %H:%M:%S',loc)
        all_time.append(locstr)
    for x in ins_history:
        xt = x['timestamp']
        tz = time.strftime('%Y-%m-%d %H:%M:%S',xt.timetuple())
        if tz in all_time:
            sym = all_time.index(tz)
            all_time[sym] = x['state']

    dfail_list = get_state_list('DEPLOYFAIL',all_time)
    stop_list = get_state_list('STOP',all_time)
    new_list = get_state_list('NEW',all_time)
    null_list = get_state_list('null',all_time)
    repair_list = get_state_list('REPAIR',all_time)
    running_list = get_state_list('RUNNING',all_time)
    unknown_list = get_state_list('UNKNOWN',all_time)
    unavail_list = get_state_list('UNAVAIL',all_time)

    result = {'dfail_list':dfail_list,'stop_list':stop_list,'new_list':new_list,'null_list':null_list,\
              'repair_list':repair_list,'running_list':running_list,'unknown_list':unknown_list,\
              'unavail_list':unavail_list,'time':start_tuple}  
    return JsonResponse(result)
