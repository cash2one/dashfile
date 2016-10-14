#!/usr/bin/python

import sys
import json

def step1(fin):
    s = json.load(fin)
    result = {}
    for k,v in s.iteritems():
        if k == 'module' or k == 'total':
            continue
        for x in v:
            type_1 = k
            type_2 = x["reason"]
            type_3 = x["hostname"]
            if type_1 not in result:
                result[type_1] = {}
            if type_2 not in result[type_1]:
                result[type_1][type_2] = {}
            if type_3 not in result[type_1][type_2]:
                result[type_1][type_2][type_3] = ""
    return result

def step1_better(result, cluster):
    # todo dict.fromkeys(listkeys, default=0)
    X = [
        'MemErr',
        'DISKIO/disk',
        'DISKIO/home',
        'DISKIO/ssd',
        'drop/disk',
        'drop/home',
        'drop/ssd',
        'ssd_noatime',
        'ssd_permission',
        'ssd_rotational',
        'ssh',
        'ip_local_port_range',
        'in_cetus_err:1',
        'in_cetus_err:2'
    ]
    fix_mac_sample = {
        'MemErr':{},
        'DISKIO/disk':{},
        'DISKIO/home':{},
        'DISKIO/ssd':{},
        'drop/disk':{},
        'drop/home':{},
        'drop/ssd':{},
        'ssd_noatime':{},
        'ssd_permission':{},
        'ssd_rotational':{},
        'ssh':{},
        'ip_local_port_range':{},
        'in_cetus_err:1':{},
        'in_cetus_err:2':{},
        'Other':{}
    }
    result_better = {}

    for k1, v1 in result.items():
        if k1 == "fix_mac":
            for k2, v2 in v1.items():
                init = False
                kthis = ""
                for k in X:
                    #if k2.startswith(k):
                    if k in k2:
                        for mm,nn in v2.items():
                            v2[mm] = k2
                        fix_mac_sample[k].update(v2)
                        kthis = k
                        init = True
                if not init:
                    for mm,nn in v2.items():
                        v2[mm] = k2
                    fix_mac_sample["Other"].update(v2)
                    kthis = "Other"
            result_better[k1] = fix_mac_sample
        elif k1 == "all_ok":
            continue
        else:
            result_better[k1] = v1
    return result_better

def step2(v3):
    list2 = []
    for k2,v2 in v3.items():
        list1 = []
        count1 = 0
        for k1,v1 in v2.items():
            list0 = []
            count0 = 0
            for k0,v0 in v1.items():
                j0 = {"id":k0,"text":k0+"("+v0.replace("'","").replace('"','')+")","icon" : "glyphicon glyphicon-link" }
                #print k0, v0
                list0.append(j0)
                count0 += 1
            count1 += count0
            j1={"id":k2+"_"+k1,"count":count0, "text":k1+" ("+str(count0)+")","icon":"glyphicon glyphicon-th-list","children":list0}
            list1.append(j1)
            list1.sort(sort_by_count)
        if k2 == "fix_mac" or k2 == "handling":
            j2={"id":k2,"count":count1,"text":k2+" ("+str(count1)+")","state":{"opened":"true"},"icon":"glyphicon glyphicon-folder-close","children":list1}
        else:
            j2={"id":k2,"count":count1,"text":k2+" ("+str(count1)+")","icon":"glyphicon glyphicon-folder-close","children":list1}
        list2.append(j2)
    list2.sort(sort_by_id)
    return list2

def sort_by_count(a,b):
    return b["count"] - a["count"]
def sort_by_id(a, b):
    #todo any unknow type is allowed
    l = ["fix_mac", "handling", "lv2cetus", "handling_onser", "some_ser_err", "fix_ser","root_passwd","guobao"]
    #l = ["fix_mac", "handling"]
    return l.index(a["id"]) - l.index(b["id"])

def main():
    stat_time = sys.argv[1]
    clusters = ['hangzhou','nanjing','shanghai','tucheng','beijing']
    for cluster in clusters:
        infile = "/home/work/data/%s/%s.machine_health.dump" % (stat_time, cluster)
        outfile = "/home/work/data_lv2/%s/%s.lv2.json" % (stat_time, cluster)
        fin = file(infile)
        fout = open(outfile, 'w')

        result = step1(fin)
        result_better = step1_better(result, cluster)
        err_jsons = step2(result_better)
        result2_json = json.dumps(err_jsons)
        print >> fout, result2_json

if __name__ == '__main__':
    main()
