#!/usr/bin/python
import MySQLdb
import os
import sys
import time

try:
    print time.localtime()
    conn = MySQLdb.connect(host='tc-ps-beehive-test1.tc.baidu.com',user='root',passwd='',db='newdb',port=3306)
    cur = conn.cursor()
    cluster_list = ['hangzhou','nanjing','shanghai','tucheng','beijing']
    month = sys.argv[1]
    day = sys.argv[2]
    hour = sys.argv[3] 
    date = '15%s%s' % (month,day)
    date_formal = '2015-%s-%s' % (month,day)
    for cluster in cluster_list:
        count = 0
        infile = '/home/work/data/%s_%s/%s.instance.list' % (date,hour,cluster)
        if os.path.exists(infile): 
            infile_agent="/home/work/data/%s_%s/%s.agent.list" % (date,hour,cluster)
            li_agent = open(infile_agent).readlines()
            dict = {}
            for x in li_agent:
                xx = x.strip('\n').split()
                if len(xx)==2:
                    dict[xx[0]]='unavail'
                else:
                    dict[xx[0]]=xx[2]
            fin = open(infile)
            for x in fin.readlines():
                data = x.strip('\n').split()
                timestamp = '%s %s:00:00' % (date_formal,hour)
                instance_id = data[0]
                command = ''
                externtion_port_begin = int(data[7])
                externtion_port_count = 90
                hostname = data[3]
                state = data[4]
                if hostname in dict.keys():
                    if dict[hostname]=='unavail':
                        state = 'UNAVAIL'
                dynamic_data = ''
                #work_path = data[5]
                heart_beat = 1
                freeze = 1
                if data[6] == 'False':
                    freeze = 0
                line = cur.execute("insert into ins_history(timestamp,instance_id,cluster,command,\
                externtion_port_begin,externtion_port_count,state,dynamic_data,hostname,heart_beat,freeze)\
                values ('%s','%s','%s','%s','%d','%d','%s','%s','%s','%d','%d')" %(timestamp,instance_id,\
                cluster,command,externtion_port_begin,externtion_port_count,state,dynamic_data,\
                hostname,heart_beat,freeze))
                count = count + line
        else:
            continue
        print "%s_%s_%s count:%s"%(date_formal,hour,cluster,count)
    conn.commit()
    cur.close()
    conn.close()
    print time.localtime()
except MySQLdb.Error,e:
    print "Mysql Error %d:%s" % (e.args[0],e.args[1])
                

