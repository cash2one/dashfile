#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json

stat_time = sys.argv[1]
cluster = sys.argv[2]

infile = "/home/work/data/%s/%s.machine_health.dump" % (stat_time, cluster)
outfile = "/home/work/data/%s/%s.machine_health_raw.list" % (stat_time, cluster)

fin = file(infile)
fout = open(outfile, 'w')

s = json.load(fin)

for k,v in s.iteritems():
    if k == 'module' or k == 'total':
        continue
    err = k
    for item in v:
        hostname = item['hostname']
        print >>fout, "%s\t%s" % (hostname, err)

