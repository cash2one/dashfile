from django.http import HttpResponse
from django.shortcuts import render_to_response
import os
import sys
sys.path.append('/home/work/dashboard/back/wangshuai14')
import make_ins_json
import uniform
from dashboard.models import InsHistory
from dashboard.models import MacHistory
import time
import json

def get_state_list(t,state_list):
    state = []
    for x in state_list:
        if x == t:
            state.append(1)
        else:
            state.append("")   
    return state

def get_mac_list(t,state_list,num):
    state = []
    for x in state_list:
        if x == t:
            state.append(num)
        else:
            state.append("")   
    return state

def index(request):
    param = request.GET   
    cluster = param.get('cluster')
    search = param.get('search')
    search_map = {search:uniform.zk(cluster)}
    for k,v in search_map.iteritems():
        if '_' not in k:    
            search_name = k
            os.system('zkcli node get --server="'+v+'" --path="/beehive/rm/machine/'+k+'/" --pretty > \
                      /home/work/data_search/machine.txt')
            os.system('zkcli node list --server="'+v+'" --path="/beehive/rm/machine/'+k+'/"  > \
                      /home/work/data_search/machine_child.txt')
            make_ins_json.main()
            infile = '/home/work/data_search/machine_child.txt'
            fin = open(infile)
            ins_name = []
            for x in fin.readlines():   
                iname = x.strip('\n')
                ins_name.append(iname)
            final_ins = []
            infile = '/home/work/data/latest/%s.instance.list' % cluster
            fin = open(infile)
            for x in fin.readlines():
                for y in ins_name:
                    x_li = x.strip('\n').split()
                    if y == x_li[0]:
                        data = x.strip('\n').split()
                        ins_href = "<a href='http://dashboard.beehive.baidu.com:8888/show_instance?search=%s&cluster=%s'\
                         target='__blank'>%s</a>" % (data[0],cluster,data[0])
                        data.append(ins_href)
                        final_ins.append(data)
            start = time.strftime('%Y-%m-%d',time.localtime(time.time()-24*3600*7))
            end = time.strftime('%Y-%m-%d',time.localtime())
            infile = '/home/work/data_search/machine.json'
            fin = open(infile)
            mac_json = json.load(fin)
            cpu_model = ''
            disk_size = ''
            ip = ''
            label = ''
            for x in mac_json:
                if x['text'].startswith('cpu_model'):
                    cpu_model = x['text']
                if x['text'].startswith('disk_size'):
                    disk_size = x['text']
                if x['text'].startswith('ip'):
                    ip = x['text']
                if x['text'] == 'label':
                    for y in x['children']:
                        label += y['text']+','
            mac_info = {'cpu_model':cpu_model.split(':'),'disk_size':disk_size.split(':'),'ip':ip.split(':'),'label':label}
            mac_start = '2015-08-11 11:00:00'
            sreal = time.strptime(mac_start,'%Y-%m-%d %H:%M:%S')
            start_tuple = (sreal[0],sreal[1]-1,sreal[2],sreal[3])
            mac_end = time.strftime('%Y-%m-%d %H',time.localtime(time.time()+8*3600))+':00:00'
            ereal = time.strptime(mac_end,'%Y-%m-%d %H:%M:%S')
            mac_history = list(MacHistory.objects.filter(hostname=search,cluster=cluster,timestamp__range=(mac_start,mac_end)))
            type1 = [] 
            type2 = []
            type3 = []
            type4 = []
            type5 = []
            type_map = {}
            ss = time.mktime(sreal)
            ee = time.mktime(ereal)
            for x in range(int(ss),int(ee)+1,3600):
                loc = time.localtime(x)
                locstr = time.strftime('%Y-%m-%d %H:%M:%S',loc)
                type1.append(locstr)
                type2.append(locstr)
                type3.append(locstr)
                type4.append(locstr)
                type5.append(locstr)
            for x in mac_history:
                xt = x.timestamp
                tz = time.strftime('%Y-%m-%d %H:%M:%S',xt.timetuple())
                if tz in type1:
                    sym = type1.index(tz)
                    type1[sym] = x.type1
                if tz in type2:
                    sym = type2.index(tz)
                    type2[sym] = x.type2
                if tz in type3:
                    sym = type3.index(tz)
                    type3[sym] = x.type3
                if tz in type4:
                    sym = type4.index(tz)
                    type4[sym] = x.type4
                if tz in type5:
                    sym = type5.index(tz)
                    type5[sym] = x.type5
            for x in type1:
                if x != None and x.startswith('2015'):
                    sym = type1.index(x)
                    type1[sym] = None
            for x in type2:
                if x != None and x.startswith('2015'):
                    sym = type2.index(x)
                    type2[sym] = None
            for x in type3:
                if x != None and x.startswith('2015'):
                    sym = type3.index(x)
                    type3[sym] = None
            for x in type4:
                if x != None and x.startswith('2015'):
                    sym = type4.index(x)
                    type4[sym] = None
            for x in type5:
                if x != None and x.startswith('2015'):
                    sym = type5.index(x)
                    type5[sym] = None
            
            type1_set = set(type1)
            type2_set = set(type2)
            type3_set = set(type3)
            type4_set = set(type4)
            type5_set = set(type5)
            for x in type1_set:
                if x != None:   
                    type_map[x] = get_mac_list(x,type1,5)
            for x in type2_set:
                if x != None:   
                    type_map[x] = get_mac_list(x,type2,4)
            for x in type3_set:
                if x != None:   
                    type_map[x] = get_mac_list(x,type3,3)
            for x in type4_set:
                if x != None:   
                    type_map[x] = get_mac_list(x,type4,2)
            for x in type5_set:
                if x != None:   
                    type_map[x] = get_mac_list(x,type5,1)
                     
            info = {'search_name':search_name,'final_ins':final_ins,'cluster':cluster,'start':start,'end':end,'mac_info':mac_info,                    'start_tuple':start_tuple,'type_map':type_map} 
            return render_to_response('machine_detail.html',info)
        else:
            search_name = k
            pos = k.rfind('_')
            os.system('zkcli node get --server="'+v+'" --path="/beehive/pd/'+k[0:pos]+'/'+k+'/status/" --pretty > \
                      /home/work/data_search/result.txt')
            os.system('zkcli node get --server="'+v+'" --path="/beehive/pd/'+k[0:pos]+'/'+k+'/" --pretty > \
                      /home/work/data_search/result_no_status.txt')
            start = time.strftime('%Y-%m-%d %H',time.localtime(time.time()-24*3600*7+8*3600))+':00:00'
            sreal = time.strptime(start,'%Y-%m-%d %H:%M:%S')
            start_tuple = (sreal[0],sreal[1]-1,sreal[2],sreal[3])
            end = time.strftime('%Y-%m-%d %H',time.localtime(time.time()+8*3600))+':00:00'
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
                      'unavail_list':unavail_list,'start_tuple':start_tuple} 
            make_ins_json.main()
            infilel = '/home/work/data_search/result.json'
            infiler = '/home/work/data_search/result_no_status.json'
            finl = open(infilel)
            finr = open(infiler)
            ljson = json.load(finl)
            rjson = json.load(finr)
            state = ''
            agent_port = ''
            begin_port = ''
            hostname = ''
            work_path = ''
            for x in ljson:
                if x['text'].startswith('state'):
                    state = x['text']
            for x in rjson:
                if x['text'].startswith('agent_port'):
                    agent_port = x['text']
                if x['text'].startswith('begin_port'):
                    begin_port = x['text']
                if x['text'].startswith('hostname'):
                    hostname = x['text']
                if x['text'].startswith('work_path'):
                    work_path = x['text']
            st_li = state.strip().split(':')
            ap_li = agent_port.strip().split(':')
            bp_li = begin_port.strip().split(':')
            ho_li = hostname.strip().split(':')
            wp_li = work_path.strip().split(':')
            ho_li[1] = "<a href='http://dashboard.beehive.baidu.com:8888/show_instance?search=%s&cluster=%s' target='__blank'>\
                       %s</a>" % (ho_li[1],cluster,ho_li[1])
            ins_info = {'state':st_li,'agent_port':ap_li,'begin_port':bp_li,'hostname':ho_li,'work_path':wp_li} 
            info = {'search_name':search_name,'result':result,'cluster':cluster,'ins_info':ins_info} 
            return render_to_response('instance_detail.html',info)

