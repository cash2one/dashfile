#!/noah/bin/python2.7
# -*- coding: utf-8 -*-
"""
get allret and zkdump data
Authors: (youxianyang@baidu.com)
"""
import os
import sys
import commands
import time
import shutil
import urllib

input_data_dir="/home/work/opbin/machine_analysis/input_data"
allret_url="nj02-www-maclife.nj02.baidu.com:/home/work/tools/auto_repair/data/"
allret_file_prefix="allretbeehive"
zk_data_dir="/home/work/opbin/zk_dump/data/dump"
zk_files={"lastest.naming":"naming", "lastest.service-instance":"service-instance", "lastest.shell":"shell", "lastest.slavenode":"slavenode"}
zk_servers={"shanghai":"sh01-ps-beehive-con1.sh01", "hangzhou":"hz01-ps-beehive-con1.hz01", "beijing":"tc-ps-beehive-con0.tc", "tucheng":"m1-ps-beehive-con0.m1", "nanjing":"nj02-ps-beehive-con1.nj02"}
cluster_info={"shanghai":"sh", "hangzhou":"hz", "tucheng":"tc", "beijing":"bj", "nanjing":"nj"}
#cluster_info={"hangzhou":"hz"}
#cluster_info={"tucheng":"tc"}

def get_data():
    #1. mkdirs    
    now = time.strftime("%Y%m%d_%H%M%S", time.localtime()) 
    data_dir = "%s/%s" % (input_data_dir, now)
    os.mkdir(now)
    wget = "wget -q --limit-rate=20M" 
    for cluster in cluster_info.keys():
        allret_filename = "%s_%s" % (allret_file_prefix, cluster)
        allret_file_url = "%s/%s" % (allret_url, allret_filename)
        allret_target_file = "%s/%s" % (data_dir, allret_filename)
        allret_cmd = "%s %s -O %s" % (wget, allret_file_url, allret_target_file)
        print allret_cmd
        (status, output) = commands.getstatusoutput(allret_cmd)
        if status == 0:
            allret_linkname = "%s/%s.latest" % (input_data_dir, allret_filename)
            create_or_modify_link(allret_target_file, allret_linkname)

        zkdownload_ok = 1
        for zkfile in zk_files.keys():
            zk_dump_file_url = "%s:%s/%s" % (zk_servers[cluster], zk_data_dir, zkfile)
            zk_dump_target_file = "%s/%s_%s" % (data_dir, cluster, zkfile)
            zk_dump_cmd = "%s %s -O %s" % (wget, zk_dump_file_url, zk_dump_target_file)
            print zk_dump_cmd
            (status, output) = commands.getstatusoutput(zk_dump_cmd)
            if status != 0:
                zkdownload_ok = 0
        if zkdownload_ok == 1:
            for zkfile in zk_files.keys():
                zk_dump_target_file = "%s/%s_%s" % (data_dir, cluster, zkfile)
                zk_linkname = "%s/%s.%s.zkdump.latest" % (input_data_dir, cluster_info[cluster], zk_files[zkfile])
                create_or_modify_link(zk_dump_target_file, zk_linkname)
        else:
            print "Fail to download zk dump files"

def create_or_modify_link(filename, linkname):
    try:
        if os.path.exists(linkname):
            os.unlink(linkname)
        if os.path.exists(filename):
            os.symlink(filename, linkname)
    except Exception as e:
        print "Fail to set link filename=[%s], linkname=[%s], exception=[%s]" % (filename, linkname, e)
        return False
    return True
    

def clean():
    if "machine_analysis" in input_data_dir:
        status, output = commands.getstatusoutput("cd %s && find . -type d -mmin +1440|xargs -i nice -19 rm -rvf {}" % input_data_dir)
        print "Clean ret", status
        print "Clean ouput", output

if __name__ == "__main__":
    try:
        get_data()
        clean()
    except Exception as e:
        print "Function Main %s", e
