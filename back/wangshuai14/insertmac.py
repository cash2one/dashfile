#!/usr/bin/python
import MySQLdb
import os
import sys
import time
import json

try:
    conn = MySQLdb.connect(host='tc-ps-beehive-test1.tc.baidu.com',user='root',passwd='',db='newdb',port=3306)
    cur = conn.cursor()
    cluster_list = ['hz','nj','sh','tc','bj']
    cluster_map = {'hz':'hangzhou','nj':'nanjing','sh':'shanghai','tc':'tucheng','bj':'beijing'}
    month = sys.argv[1]
    day = sys.argv[2]
    hour = sys.argv[3]
    date = '2015-%s-%s' % (month,day)
    timestamp = '2015-%s-%s %s:00:00' % (month,day,hour)
    for cluster in cluster_list:
        label = ''
        jifang = cluster_map[cluster]
        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.ATLEAST_1_RUNNING' % (date,hour,cluster)
        fin = open(infile)
        unavail_notinerr = json.load(fin)
        type1 = 'machine_used'
        available = 1
        for k,v in unavail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1) values ('%s','%s','%s',\
                '%s','%d','%s')"%(timestamp,jifang,hostname,label,available,type1))


        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.unavailable.inerr.with_ERR_CLASS' % (date,hour,cluster)
        fin = open(infile)
        unavail_inerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_unavailable'
        type3 = 'inerr'
        available = 0
        for k,v in unavail_inerr.iteritems():
            hostname = k
            for k1,v1 in v.iteritems():
                type4 = v1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4) values \
                           ('%s','%s','%s','%s','%d','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,\
                           type3,type4))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.unavailable.NOTinerr' % (date,hour,cluster)
        fin = open(infile)
        unavail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_unavailable'
        type3 = 'NOTinerr'
        available = 0
        for k,v in unavail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3) values \
                           ('%s','%s','%s','%s','%d','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,type3))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.inerr.with_ERR_CLASS' % (date,hour,cluster)
        fin = open(infile)
        avail_inerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'inerr'
        available = 1
        for k,v in avail_inerr.iteritems():
            hostname = k
            for k1,v1 in v.iteritems():
                type4 = v1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4) values \
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,type3,type4))
           
        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER' % (date,hour,cluster)
        fin = open(infile)
        avail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'NOTinerr'
        type4 = 'NO_CONTAINER'
        available = 1
        for k,v in avail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4) values \
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,type3,type4))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE'% (date,hour,cluster)
        fin = open(infile)
        avail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'NOTinerr'
        type4 = 'HAS_CONTAINER' 
        type5 = 'ONLY_HAS_STOP_INSTANCE'
        available = 1
        for k,v in avail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4,type5) values\
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,\
                type3,type4,type5))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE'% (date,hour,cluster)
        fin = open(infile)
        avail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'NOTinerr'
        type4 = 'HAS_CONTAINER' 
        type5 = 'ONLY_HAS_NOT_STOP_INSTANCE'
        available = 1
        for k,v in avail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4,type5) values\
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,type1,type2,type3,\
                type4,type5))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE' % (date,hour,cluster)
        fin = open(infile)
        avail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'NOTinerr'
        type4 = 'HAS_CONTAINER' 
        type5 = 'HAS_STOP_AND_NOT_STOP_INSTANCE'
        available = 1
        for k,v in avail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4,type5) values\
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,\
                type1,type2,type3,type4,type5))

        infile = '/home/work/data_unused_machine/data/analyse_machine_userate/%s/%s/%s.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE'% (date,hour,cluster)
        fin = open(infile)
        avail_notinerr = json.load(fin)
        type1 = 'machine_unused'
        type2 = 'machine_available_but_no_running'
        type3 = 'NOTinerr'
        type4 = 'HAS_CONTAINER' 
        type5 = 'ONLY_HAS_NO_PD_INSTANCE'
        available = 1
        for k,v in avail_notinerr.iteritems():
            for k1,v1 in v.iteritems():
                hostname = k1
                cur.execute("insert into mac_history(timestamp,cluster,hostname,label,available,type1,type2,type3,type4,type5) values\
                ('%s','%s','%s','%s','%d','%s','%s','%s','%s','%s')"%(timestamp,jifang,hostname,label,available,\
                type1,type2,type3,type4,type5))

    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error,e:
    print "Mysql Error %d:%s" % (e.args[0],e.args[1])
                

