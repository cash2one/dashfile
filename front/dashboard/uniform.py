#!/usr/bin/python
#coding=gbk

def cluster():
    return ['hangzhou','nanjing','shanghai','tucheng','beijing']

def cluster_short():
    return ['hz','nj','sh','tc','bj']

def zk(cluster):
    zk_map = { 'hangzhou':'10.211.47.19:2181','nanjing':'10.207.46.44:2181','shanghai':'10.202.254.31:2181','tucheng':'10.42.208.21:2181','beijing':'10.36.130.64:2181'}
    return zk_map[cluster]

def module():
    return ['bs','bc','attr','basa','dictserver','disp','bs_on_ns']

def mrate():
    return ['all','online','hard','soft','no_err','no_err_use']

def mrate_better():
    return {"all":u'总使用率', "online":u'标记online率', "hard":u'硬故障率', "soft":u'软故障率', "no_err":u'无故障率', "no_err_use":u'无故障使用率'}

def agent():
    return ["all", "no_hard_err"]
def get_path():
    return '/home/work/dashboard/back/'
