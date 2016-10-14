#!/usr/bin/python

import MySQLdb
import datetime
import math
try:
    conn=MySQLdb.connect(host='tc-ps-beehive-test1.tc.baidu.com',user='root',passwd='',db='newdb',port=3306)
    cur=conn.cursor()
    today=datetime.datetime.today()
    tmp=today.isoformat()
    this_mon=tmp[2:4]+tmp[5:7]
    this_day=this_mon+tmp[8:10]
    stat_time=this_day+'_'+tmp[11:13]
    cluster=['hangzhou','nanjing','shanghai','tucheng','beijing']
    for c in cluster:
        cur.execute("select avg(k.running_rate) from (select * from stat_machine where cluster='%s' and label='*all*'\
                     order by stat_time desc limit 0,24)k "% c)
        ll=cur.fetchone()
        latest_24=round(ll[0],2)
        cur.execute("select avg(k.running_rate) from (select * from stat_machine where cluster='%s' and label='*all*'\
                     and stat_time like '%s%%')k"% (c,this_mon) )
        ll=cur.fetchone()
        day_30=round(ll[0],2)
        cur.execute("select avg(k.running_rate) from (select * from stat_machine where cluster='%s' and label='*all*'\
                     order by stat_time desc limit 0,720)k "% c)
        ll=cur.fetchone()
        latest_30=round(ll[0],2)
        cur.execute("insert into kpi_machine(stat_time,cluster,latest_24,day_30,latest_30) \
                     values('%s','%s','%s','%s','%s')"%(stat_time,c,latest_24,day_30,latest_30))
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error,e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])



