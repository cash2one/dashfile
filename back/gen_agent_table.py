#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys

stat_time=sys.argv[1]

clusters=['beijing','hangzhou','nanjing','shanghai','tucheng']

format_1 = "%s\t%d\t%.2f%%\t%d\t%.2f%%"
format_2 = "\t%s\t%s\t%d\t%.2f\t%d\t%.2f"
outfile_1 = "/home/work/data/%s/agent.table" % stat_time
outfile_2 = "/home/work/data/%s/agent.table.sql" % stat_time
fout_1 = open(outfile_1, 'w')
fout_2 = open(outfile_2, 'w')

def calc(fenzi, fenmu):
    if fenmu == 0:
        return 0.0
    return float(fenzi)/fenmu*100

total = {}
total['all'] = 0
total['available'] = 0
total['no_err'] = 0
total['no_err_available'] = 0

for cluster in clusters:
  err_map = {}
  fe = open('/home/work/data/'+stat_time+'/'+cluster+'.machine_err.list')
  for line in fe.readlines():
    s = line.strip().split('\t')
    err_map[s[0]] = s[1]

  result = {}
  result['all'] = 0
  result['available'] = 0
  result['no_err'] = 0
  result['no_err_available'] = 0

  fa = open('/home/work/data/'+stat_time+'/'+cluster+'.agent.list')
  for line in fa.readlines():
    s = line.strip().split('\t')
    hostname = s[0]
    agent_state = s[2]
    result['all'] += 1
    if agent_state == 'avail':
        result['available'] += 1
    if hostname not in err_map:
        result['no_err'] += 1
        if agent_state == 'avail':
            result['no_err_available'] += 1

  total['all'] += result['all']
  total['available'] += result['available']
  total['no_err'] += result['no_err']
  total['no_err_available'] += result['no_err_available']

  tuple_1 = (cluster,
          result['all'], calc(result['available'], result['all']),
          result['no_err'], calc(result['no_err_available'], result['no_err']))
  tuple_2 = (stat_time,) + tuple_1
  print >>fout_1, format_1 % tuple_1
  print >>fout_2, format_2 % tuple_2


tuple_1 = ("*all*",
        total['all'], calc(total['available'], total['all']),
        total['no_err'], calc(total['no_err_available'], total['no_err']))
tuple_2 = (stat_time,) + tuple_1
print >>fout_1, format_1 % tuple_1
print >>fout_2, format_2 % tuple_2

