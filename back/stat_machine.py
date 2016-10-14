#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json

stat_time = sys.argv[1]
cluster = sys.argv[2]

infile = "/home/work/data/%s/%s.machine.dump" % (stat_time, cluster)
outfile = "/home/work/data/%s/%s.machine.list" % (stat_time, cluster)

fin = file(infile)
fout = open(outfile, 'w')

s = json.load(fin)

for k,v in s['sons']['machine']['sons'].iteritems():
    if k == 'global':
        continue

    #hostname
    hostname = k

    #state
    meta = v['meta']
    if 'state' in meta:
        state = meta['state']
    else:
        state = 'null'

    #label
    if 'label' in meta and len(meta['label']) > 0:
        label = ','.join(meta['label'])
    else:
        label = 'null'

    #print
    print >> fout, "%s\t%s\t%s" % (hostname, state, label)

