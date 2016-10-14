#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json

stat_time = sys.argv[1]
cluster = sys.argv[2]

infile = "/home/work/data/%s/%s.machine_health.dump" % (stat_time, cluster)

file_object = open(infile)
try:
    all_the_text = file_object.read()
    file_object.close()

    index = all_the_text.rfind('}')
    new = all_the_text[0:index + 1]
    file_object = open(infile, 'w')
    file_object.write(new)
finally:
    file_object.close()
