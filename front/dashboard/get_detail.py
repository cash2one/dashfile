#coding=gbk
import datetime
import time
from dashboard.models import StatInstance
from dashboard.models import StatAgent
from dashboard.models import YjMachine
from dashboard.models import StatMachineNew
def getinfo_detail(request,jifang):
    stat_time = time.strftime('%y%m%d_%H',time.localtime(time.time()+7*3600))
    today = datetime.datetime.today()
    strtime = time.strftime('%Y-%m-%d',time.localtime())
    d = 'day_'+strtime
    #yj machine list
    yjl = list(YjMachine.objects.filter(cluster=jifang).order_by("-stat_time")[0:200])
    yj_table = []
    for x in yjl:
        if len(yj_table) == 0:
            yj_table.append(x)
        else:
            last = yj_table[-1]
            if x.fix_mac != last.fix_mac or \
                x.handling != last.handling or \
                x.not_found != last.not_found or \
                x.all_ok != last.all_ok or \
                x.fix_ser != last.fix_ser or \
                x.handling_onser != last.handling_onser or \
                x.lv2cetus != last.lv2cetus or \
                x.some_ser_err != last.some_ser_err:
                yj_table.append(x)
    yj_table = yj_table[0:18]
    #qst_datetime
    start = 0
    end = 24
    d_li = d.split('_')
    ymd = time.strptime(d_li[1],'%Y-%m-%d')
    dt = datetime.datetime(ymd[0],ymd[1],ymd[2])
    result = today-dt
    d_get = result.days
    day_x = today-datetime.timedelta(days=d_get+1)
    start = d_get*24
    end = start+24
    #qst_machine  
    tuple_day_mac = (day_x.year,day_x.month-1,day_x.day,day_x.hour+8)
    qst_mac = list(StatMachineNew.objects.filter(cluster=jifang,label='*all*').order_by("-stat_time")[start:end])
    qst_mac.reverse()
    qsm = [] 
    for x in qst_mac:
        qsm.append(x.running_rate)
    time_mac = []
    for t in qst_mac:
        time_mac.append(t.stat_time)

    #qst_instance 
    tuple_day_ins = (day_x.year,day_x.month-1,day_x.day,day_x.hour+8)
    qst_ins = list(StatInstance.objects.filter(cluster=jifang,module='bs').order_by("-stat_time")[start:end])
    qst_ins.reverse()
    qsi = []
    for x in qst_ins:
        qsi.append(100-x.live_rate)
    time_ins = []
    for t in qst_ins:
        time_ins.append(t.stat_time)
    
    #qst_agent 
    tuple_day_agent = (day_x.year,day_x.month-1,day_x.day,day_x.hour+8)
    qst_agent = list(StatAgent.objects.filter(cluster=jifang).order_by("-stat_time")[start:end])
    qst_agent.reverse()
    
    qsa = [] 
    for x in qst_agent:
        qsa.append(x.all_avail_rate)

    time_agent = []
    for t in qst_agent:
        time_agent.append(t.stat_time)
    
    #machine_label
    ml = list(StatMachineNew.objects.filter(cluster=jifang,stat_time=stat_time).values('label'))
    labels = []
    for x in ml:
        lab = x['label'].encode()
        labels.append(lab)

    #return 
    return [yj_table,qsm,qsi,time_mac,time_ins,tuple_day_mac,tuple_day_ins,qsa,time_agent,tuple_day_agent,labels]

def mysort(x,y):
    a = x[0].split('_')
    b = y[0].split('_')
    a_time = time.strptime(a[1],'%Y-%m-%d')
    b_time = time.strptime(b[1],'%Y-%m-%d')
    a_stamp = time.mktime(a_time)
    b_stamp = time.mktime(b_time)
    return int(a_stamp)-int(b_stamp)

today = datetime.datetime.today()
zuotian = today-datetime.timedelta(days=1)
qiantian = today-datetime.timedelta(days=2)
shangzhou = today-datetime.timedelta(days=7)
shangyue = today-datetime.timedelta(days=30) 

def daylist():
    global today,zuotian,qiantian
    daylist = []
    daydict = {}
    for x in [0,1,2,3,4,5]:
        y = today - datetime.timedelta(days=x)
        daydict["day_"+str(y.year)+'-'+str(y.month)+"-"+str(y.day)] = [str(y.month) + "-" + str(y.day)]
    daylist = daydict.items()
    daylist.sort(mysort,reverse=True)
    for v in daylist:
        if v[1][0] == str(today.month)+'-'+str(today.day):
            v[1][0] = u'今天'
        elif v[1][0] == str(zuotian.month)+'-'+str(zuotian.day):
            v[1][0] = u'昨天'
        elif v[1][0] == str(qiantian.month)+'-'+str(qiantian.day):
            v[1][0] = u'前天'
        else:
            pass
    return daylist

def weeklist():
    global today,shangzhou
    weeklist = []
    weekdict = {}
    for x in [0,7,14,21]:
        w = today-datetime.timedelta(days=x)
        weekdict['week_'+str(w.year)+'-'+str(w.month)+'-'+str(w.day)] = [str(w.month)+'-'+str(w.day)]
    weeklist = weekdict.items()
    weeklist.sort(mysort,reverse=True)
    for v in weeklist:
        if v[1][0] == str(today.month)+'-'+str(today.day):
            v[1][0] = u'本周'
        elif v[1][0] == str(shangzhou.month)+'-'+str(shangzhou.day):
            v[1][0] = u'上周'
        else:
            pass
    return weeklist 

def monthlist():
    global today,shangyue
    monthlist = []
    monthdict = {}
    for x in [0,1]:
        m = today-datetime.timedelta(days=x*30)
        monthdict['mon_'+str(m.year)+'-'+str(m.month)+'-'+str(m.day)] = [str(m.month)+'-'+str(m.day)]
    monthlist = monthdict.items()
    monthlist.sort(mysort,reverse=True)
    for v in monthlist:
        if v[1][0] == str(today.month)+'-'+str(today.day):
            v[1][0] = u'本月'
        elif v[1][0] == str(shangyue.month)+'-'+str(shangyue.day):
            v[1][0] = u'上月'
        else:
            pass
    return monthlist
