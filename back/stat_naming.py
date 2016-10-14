#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys

stat_time=sys.argv[1]
cluster=sys.argv[2]

outfile = "/home/work/data/%s/%s.naming.list" % (stat_time, cluster)
fout = open(outfile, 'w')

ins_map = {}
fh = open('/home/work/data/'+stat_time+'/'+cluster+'.instance.list')
for line in fh.readlines():
  s = line.strip().split('\t')
  ins_id = s[0]
  ip = s[3]
  port = s[7]
  host = ip + ':' + port
  ins_map[host] = ins_id

fh = open('/home/work/data/'+stat_time+'/'+cluster+'.naming_raw.list')
for line in fh.readlines():
  s = line.strip().split('\t')
  app_id = s[0]
  ip = s[1]
  port = s[2]
  host = ip + ':' + port
  if host in ins_map:
    print >>fout, "%s\t%s\t%s\t%s" % (app_id, ip, port, ins_map[host])

