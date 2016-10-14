from dashboard.models import StatMachine
from dashboard.models import KpiInstance
from dashboard.models import KpiMachine
from dashboard.models import NsTotal
import uniform
import sys
import os

def getinfo(request,jifang):
    #kpi
    kpi_machine = list(KpiMachine.objects.filter(cluster=jifang).order_by("-stat_time")[0:1])
    kpi_instance = list(KpiInstance.objects.filter(cluster=jifang).order_by("-stat_time")[0:1])
    #machine, instance
    machine_today = list(reversed(list(StatMachine.objects.filter(cluster=jifang,label='*all*').order_by("-stat_time")[0:24])))
    machine_yes = list(reversed(list(StatMachine.objects.filter(cluster=jifang,label='*all*').order_by("-stat_time")[24:48])))
    instance_today = list(reversed(list(NsTotal.objects.filter(room=jifang).order_by("-time")[0:24])))
    instance_yes = list(reversed(list(NsTotal.objects.filter(room=jifang).order_by("-time")[24:48])))
    mt = [] 
    for x in machine_today:
        mt.append(x.running_rate)
    my = []
    for x in machine_yes:
        my.append(x.running_rate)
    it = []
    for x in instance_today:
        it.append(round(x.live_rate*100,2))
    iy = []
    for x in instance_yes:
        iy.append(round(x.live_rate*100,2))
    mac_time = []
    for t in machine_today:
       mac_time.append(t.stat_time[-2:])
    ins_time = []
    for t in instance_today:
       ins_time.append(t.time[-2:])
    return [mt,my,it,iy,mac_time,ins_time,kpi_machine,kpi_instance]

def getdata(request):
    list_str = {
        "machine":[],
        "instance":[],
        "sym1":'%',
        "sym2":'%',
        "kpi_machine":[],
        "kpi_instance":[]
    }
    l = uniform.cluster()
    for x in l:
        ret =getinfo(request,x)
        labelm = 'machine' + str(l.index(x) + 1)
        labeli = 'instance' + str(l.index(x) + 1)
        machine = [labelm, ret[4], ret[0], ret[1]]
        instance = [labeli, ret[5], ret[2], ret[3]]
        list_str['machine'].append(machine)
        list_str['instance'].append(instance)
        list_str['kpi_machine'].append(ret[6])
        list_str['kpi_instance'].append(ret[7])
    return list_str

def mcsort(a,b):
    mrate = uniform.mrate()
    x = mrate.index(a[0])
    y = mrate.index(b[0])
    return x-y

def sort_cluster(a,b):
    clist = uniform.cluster()
    x = clist.index(a[0])
    y = clist.index(b[0])
    return x-y

PATH = uniform.get_path()

def get_core():
    global PATH
    core_map = {}
    for x in uniform.cluster():
        core_map[x] = {}
    if os.path.exists(PATH+'version_info'):
        file_version = open(PATH+'version_info')
        for line in file_version:
            line = line.strip('\n')
            x = line.split()
            cluster = x[0]
            shell_pd_rm = x[1]
            version = x[2]
            if len(x) < 3:
                core_map[cluster][shell_pd_rm] = '??'
            else:
                core_map[cluster][shell_pd_rm] = version
    else:
        for x in uniform.cluster():
            core_map[x]['shell'] = '??'
            core_map[x]['pd'] = '??'
            core_map[x]['rm'] = '??'
    file_main = open(PATH+'main.list')
    for line in file_main:
        line = line.strip('\n')
        x = line.split()
        cluster = x[0]
        host = x[1]
        core_map[cluster]['main'] = host
    file_backup = open(PATH+'vice.list')
    for line in file_backup:
        line = line.strip('\n')
        x = line.split()
        cluster = x[0]
        host = x[1]
        core_map[cluster]['backup'] = host
    file_zk = open(PATH+'zk.list')
    for line in file_zk:
        line = line.strip('\n')
        x = line.split()
        cluster = x[0]
        host = x[1]
        core_map[cluster]['zk'] = host
        
    l = core_map.items()
    l.sort(sort_cluster)
    return l

def get_history():
    history = []
    history_err = []
    f = open('/home/work/data/latest/history')
    for line in f:
        x = line.strip('\n').split()
        if len(x) < 3:
            history.extend([[x[0],x[1],'??']])
        else:
            history.extend([[x[0],x[1],x[2]]])
    for x in history:
        if x[1] == 'err':
            history_err.append(x)
    return history_err

def get_zk_info():
    global PATH
    infile = PATH+"zk_info.list"
    fin = open(infile)
    zk_map = {}
    for x in fin.readlines():
        x = x.strip('\n')
        pos = x.find(':')
        zk_map[x[0:pos]] = x[pos+2:]
    return zk_map
