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
    count_day_30=cur.execute("select * from stat_instance where cluster='hangzhou' and module='*core*'\
                              and stat_time like '%s%%'"%this_mon)
    count_day_30=int(math.ceil(count_day_30*0.05))-1
    cluster=['hangzhou','nanjing','shanghai','tucheng','beijing']
    for c in cluster:
        cur.execute("select k.live_rate from (select * from stat_instance where cluster='%s' and module='*core*'\
                     order by stat_time desc limit 0,24)k order by live_rate  "% c)
        ll=cur.fetchall()
        per_24=round(ll[1][0],2)
        cur.execute("select k.live_rate from (select * from stat_instance where cluster='%s' and module='*core*'\
                     and stat_time like '%s%%')k order by live_rate  "% (c,this_mon))
        ll=cur.fetchall()
        per_day_30=round(ll[count_day_30][0],2)
        cur.execute("select k.live_rate from (select * from stat_instance where cluster='%s' and module='*core*'\
                     order by stat_time desc limit 0,720)k order by live_rate "% c)
        ll=cur.fetchall()
        per_latest_30=round(ll[35][0],2)
        cur.execute("insert into kpi_instance(stat_time,cluster,per_24,per_day_30,per_latest_30) \
                     values('%s','%s','%s','%s','%s')"%(stat_time,c,per_24,per_day_30,per_latest_30))
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error,e:
    print "Mysql Error %d: %s" % (e.args[0], e.args[1])



