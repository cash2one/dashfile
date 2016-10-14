#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json

stat_time = sys.argv[1]
cluster = sys.argv[2]

infile = "/home/work/data/%s/%s.naming.dump" % (stat_time, cluster)
outfile = "/home/work/data/%s/%s.naming_raw.list" % (stat_time, cluster)

fin = file(infile)
fout = open(outfile, 'w')

s = json.load(fin)

for k,v in s['sons'].iteritems():
    if k == 'global':
        continue

    #hostname
    app_id = k
    if not app_id.startswith('bs_'):
        continue

    #state
    meta = v['meta']
    if 'overlay_first' in meta:
        overlay_first = meta['overlay_first']
    else:
        overlay_first = None

    if not overlay_first:
        print "ERROR: [%s] overlay_first is not True, but %s" % (app_id, overlay_first)
        continue

    if 'overlay' not in v['sons']:
        print "ERROR: [%s] overlay not exist" % app_id
        continue

    for i in v['sons']['overlay']['meta']['items']:
        ip = i['ip']
        port = i['port']
        print >> fout, "%s\t%s\t%s" % (app_id, ip, port)

