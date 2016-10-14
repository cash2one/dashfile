#!/usr/bin/python
# vim: set fileencoding=gb2312
import time
local_time=time.localtime()
stat_time=time.strftime('%y%m%d_%H',local_time)

clusters=['beijing','hangzhou','nanjing','shanghai','tucheng']

format_1 = "%s\t%s\t%d\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%\t%.2f%%"
format_2 = "\t%s\t%s\t%s\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f"
outfile_1 = "/home/work/data_ml/machine.table"
outfile_2 = "/home/work/data_ml/machine.table.sql"
fout_1 = open(outfile_1, 'w')
fout_2 = open(outfile_2, 'w')

def calc(fenzi, fenmu):
    if fenmu == 0:
        return 0.0
    return float(fenzi)/fenmu*100


for cluster in clusters:
    labels=['*all*']
    labelfile="/home/work/data_ml/"+cluster+".machine_label.list"
    ll=open(labelfile).readlines()
    for line in ll:
        line=line.strip().split()
        labels.append(line[1])
    agent_map = {}
    fa = open('/home/work/data/latest/'+cluster+'.agent.list')
    for line in fa.readlines():
        s = line.strip().split('\t')
        agent_map[s[0]] = s[2]


    err_map = {}
    fe = open('/home/work/data/latest/'+cluster+'.machine_err.list')
    for line in fe.readlines():
        s = line.strip().split('\t')
        err_map[s[0]] = s[1]


    all_ins_map = {}
    running_ins_map = {}
    for i in agent_map.iterkeys():
        all_ins_map[i] = 0
        running_ins_map[i] = 0

    fi = open('/home/work/data/latest/'+cluster+'.instance.list')
    for line in fi.readlines():
        s = line.strip().split('\t')
        hostname = s[3]
        state = s[4]
        if hostname not in all_ins_map:
            continue
        all_ins_map[hostname] += 1
        if state == 'RUNNING':
            running_ins_map[hostname] += 1


    result_map = {}
    for i in labels:
        result_map[i] = {}
        result_map[i]['all_count'] = 0  #总机器数
        result_map[i]['online_count'] = 0 #标记为online的机器数
        result_map[i]['hard_err_count'] = 0 #硬故障机器数
        result_map[i]['soft_err_count'] = 0 #软故障机器数
        result_map[i]['no_err_count'] = 0 #无故障机器数
        result_map[i]['no_err_running_count'] = 0 #运行有实例的无故障机器数
        result_map[i]['running_count'] = 0 #运行有实例的机器数


    fm=open('/home/work/data/latest/'+cluster+'.machine.list')
    for line in fm.readlines():
        s = line.strip().split('\t')
        hostname = s[0]
        state = s[1]
        label = s[2]
        all_count = 1

        if state == 'online':
            online_count = 1
        else:
            online_count = 0

        if hostname in err_map:
            hard_err_count = 1
        else:
            hard_err_count = 0

        if (hostname not in err_map and
                (agent_map[hostname] == 'unavail' or
                    (all_ins_map[hostname] > 0 and running_ins_map[hostname] == 0))):
            soft_err_count = 1
        else:
            soft_err_count = 0

        if (hostname not in err_map and agent_map[hostname] == 'avail' and
                (all_ins_map[hostname] == 0 or running_ins_map[hostname] > 0)):
            no_err_count = 1
        else:
            no_err_count = 0

        if no_err_count > 0 and running_ins_map[hostname] > 0:
            no_err_running_count = 1
        else:
            no_err_running_count = 0

        if (agent_map[hostname] == 'avail' and running_ins_map[hostname] > 0):
            running_count = 1
        else:
            running_count = 0

        cur_labels = ['*all*']
        if label in labels and label not in cur_labels:
            cur_labels.append(label)
        for i in cur_labels:
            result_map[i]['all_count'] += all_count
            result_map[i]['online_count'] += online_count
            result_map[i]['hard_err_count'] += hard_err_count
            result_map[i]['soft_err_count'] += soft_err_count
            result_map[i]['no_err_count'] += no_err_count
            result_map[i]['no_err_running_count'] += no_err_running_count
            result_map[i]['running_count'] += running_count
    for label in labels:
        r = result_map[label]
        tuple_1 = (cluster, label, r['all_count'],
                calc(r['online_count'], r['all_count']),
                calc(r['hard_err_count'], r['all_count']),
                calc(r['soft_err_count'], r['all_count']),
                calc(r['no_err_count'], r['all_count']),
                calc(r['no_err_running_count'], r['no_err_count']),
                calc(r['running_count'], r['all_count']))
        tuple_2 = (stat_time,) + tuple_1
        print >>fout_1, format_1 % tuple_1
        print >>fout_2, format_2 % tuple_2


