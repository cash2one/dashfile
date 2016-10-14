#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys

stat_time=sys.argv[1]

clusters=['beijing','hangzhou','nanjing','shanghai','tucheng']
core_modules=['basa','bc','bs','disp','attr','dictserver']
modules=['*all*','*core*']+core_modules

format_1 = "%s\t%s\t%d\t%.2f%%\t%d\t%.2f%%"
format_2 = "\t%s\t%s\t%s\t%d\t%.2f\t%d\t%.2f"
outfile_1 = "/home/work/data/%s/instance.table" % stat_time
outfile_2 = "/home/work/data/%s/instance.table.sql" % stat_time
fout_1 = open(outfile_1, 'w')
fout_2 = open(outfile_2, 'w')

def calc(fenzi, fenmu):
    if fenmu == 0:
        return 0.0
    return float(fenzi)/fenmu*100

total_all_map = {}
total_live_map = {}
total_naming_all_map = {}
total_naming_live_map = {}
for m in modules:
    total_all_map[m] = 0
    total_live_map[m] = 0
    total_naming_all_map[m] = 0
    total_naming_live_map[m] = 0

for cluster in clusters:
  agent_map = {}
  fa = open('/home/work/data/'+stat_time+'/'+cluster+'.agent.list')
  for line in fa.readlines():
    s = line.strip().split('\t')
    agent_map[s[0]] = s[2]

  naming_map = {}
  fn = open('/home/work/data/'+stat_time+'/'+cluster+'.naming.list')
  for line in fn.readlines():
    s = line.strip().split('\t')
    naming_map[s[3]] = s[0]

  all_map = {}
  live_map = {}
  naming_all_map = {}
  naming_live_map = {}
  for m in modules:
      all_map[m] = 0
      live_map[m] = 0
      naming_all_map[m] = 0
      naming_live_map[m] = 0

  fi = open('/home/work/data/'+stat_time+'/'+cluster+'.instance.list')
  for line in fi.readlines():
    s = line.strip().split('\t')
    ins_id = s[0]
    module = s[1]
    app_id = s[2]
    hostname = s[3]
    run_state = s[4]
    work_path = s[5]

    live = 0
    if (hostname in agent_map
            and agent_map[hostname] == 'avail'
            and run_state == 'RUNNING'):
        live = 1

    cur_modules = ['*all*']
    if module in core_modules:
        cur_modules.append('*core*')
        cur_modules.append(module)

    for module in cur_modules:
        all_map[module] += 1
        live_map[module] += live
        total_all_map[module] += 1
        total_live_map[module] += live
        if module == 'bs' and ins_id in naming_map:
            naming_all_map[module] += 1
            naming_live_map[module] += live
            total_naming_all_map[module] += 1
            total_naming_live_map[module] += live

  for m in modules:
    tuple_1 = (cluster, m, all_map[m], calc(live_map[m], all_map[m]),
            naming_all_map[m], calc(naming_live_map[m], naming_all_map[m]))
    tuple_2 = (stat_time,) + tuple_1
    print >>fout_1, format_1 % tuple_1
    print >>fout_2, format_2 % tuple_2


for m in modules:
    tuple_1 = ("*all*", m, total_all_map[m], calc(total_live_map[m], total_all_map[m]),
            total_naming_all_map[m], calc(total_naming_live_map[m], total_naming_all_map[m]))
    tuple_2 = (stat_time,) + tuple_1
    print >>fout_1, format_1 % tuple_1
    print >>fout_2, format_2 % tuple_2

