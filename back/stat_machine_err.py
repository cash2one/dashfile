#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys

stat_time=sys.argv[1]
cluster=sys.argv[2]

err_tags=['fix_mac','handling']

outfile = "/home/work/data/%s/%s.machine_err.list" % (stat_time, cluster)
fout = open(outfile, 'w')

health_map = {}
fh = open('/home/work/data/'+stat_time+'/'+cluster+'.machine_health.list')
for line in fh.readlines():
  s = line.strip().split('\t')
  hostname = s[0]
  ip = s[1]
  err = s[2]
  if hostname in health_map:
    health_map[hostname].append(err)
  else:
    health_map[hostname] = [err]
  if ip in health_map:
    health_map[ip].append(err)
  else:
    health_map[ip] = [err]

fh = open('/home/work/data/'+stat_time+'/'+cluster+'.machine.list')
for line in fh.readlines():
  s = line.strip().split('\t')
  hostname = s[0]
  if hostname not in health_map:
    print >>fout, "%s\t%s" % (hostname, "not_found")
    continue
  err_list = health_map[hostname]
  matched_err_tags = []
  for e in err_tags:
    if e in err_list:
      matched_err_tags.append(e)
  if len(matched_err_tags) > 0:
    print >>fout, "%s\t%s" % (hostname, ','.join(matched_err_tags))

