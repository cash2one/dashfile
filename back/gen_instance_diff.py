#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json

stat_time=sys.argv[1]
cluster=sys.argv[2]

modules=['basa','bc','bs','disp','attr','dictserver']

infile = "/home/work/data/%s/%s.instance.data" % (stat_time, cluster)
agentfile = "/home/work/data/%s/%s.agent.list" % (stat_time, cluster)

agent_map = {}
fagent = file(agentfile)
for line in fagent.readlines():
    s = line.strip().split('\t')
    agent_map[s[0]] = s[2]

fin = file(infile)
s = json.load(fin)

for module in modules:
    apps = {}
    for k,v in s.iteritems():
        app_id = k
        if v['module'] != module:
            continue
        app = {}
        apps[app_id] = app
        app['instances'] = []
        app['package_data_source'] = {}
        app['static_data'] = {}
        app['dynamic_data'] = {}
        for k1,v1 in v['instances'].iteritems():
            ins_id = k1
            hostname = v1['hostname']
            if (hostname not in agent_map
                    or agent_map[hostname] != 'avail'
                    or v1['run_state'] != 'RUNNING'):
                continue
            app['instances'].append(ins_id)
            data = "{%s}" % v1['package_data_source']
            if data not in app['package_data_source']:
                app['package_data_source'][data] = []
            app['package_data_source'][data].append(ins_id)
            for k2,v2 in v1['static_data'].iteritems():
                name = k2
                if name not in app['static_data']:
                    app['static_data'][name] = {}
                data = "{%s}{%s}" % (v2['data_source'], v2['timestamp'])
                if data not in app['static_data'][name]:
                    app['static_data'][name][data] = []
                app['static_data'][name][data].append(ins_id)
            for k2,v2 in v1['dynamic_data'].iteritems():
                name = k2
                if name not in app['dynamic_data']:
                    app['dynamic_data'][name] = {}
                data = "{%s}{%s}" % (v2['data_source'], v2['timestamp'])
                if data not in app['dynamic_data'][name]:
                    app['dynamic_data'][name][data] = []
                app['dynamic_data'][name][data].append(ins_id)
    
    diff = {}
    for k,v in apps.iteritems():
        app_id = k
        app = v
        app_diff = {}
        app_diff['package_data_source'] = {}
        app_diff['static_data'] = {}
        app_diff['dynamic_data'] = {}
        instances = app['instances']
        ins_count = len(instances)
        if len(app['package_data_source']) > 1:
            for data,ins_list in app['package_data_source'].iteritems():
                app_diff['package_data_source'][data] = "%d instances, like [%s]" % \
                        (len(ins_list), ','.join(ins_list[0:1]))
        for name,datas in app['static_data'].iteritems():
            exist_list = []
            for data,ins_list in datas.iteritems():
                exist_list += ins_list
            not_found = False
            if len(exist_list) != ins_count:
                not_found = True
                if name not in app_diff['static_data']:
                    app_diff['static_data'][name] = {}
                not_found_list = [val for val in instances if val not in exist_list]
                app_diff['static_data'][name]['not_found'] = "%d instances, like [%s]" % \
                        (len(not_found_list), ','.join(not_found_list[0:1]))
            if not_found or len(datas) > 1:
                if name not in app_diff['static_data']:
                    app_diff['static_data'][name] = {}
                for data,ins_list in datas.iteritems():
                    app_diff['static_data'][name][data] = "%d instances, like [%s]" % \
                            (len(ins_list), ','.join(ins_list[0:1]))
        for name,datas in app['dynamic_data'].iteritems():
            exist_list = []
            for data,ins_list in datas.iteritems():
                exist_list += ins_list
            not_found = False
            if len(exist_list) != ins_count:
                not_found = True
                if name not in app_diff['dynamic_data']:
                    app_diff['dynamic_data'][name] = {}
                not_found_list = [val for val in instances if val not in exist_list]
                app_diff['dynamic_data'][name]['not_found'] = "%d instances, like [%s]" % \
                        (len(not_found_list), ','.join(not_found_list[0:1]))
            if not_found or len(datas) > 1:
                if name not in app_diff['dynamic_data']:
                    app_diff['dynamic_data'][name] = {}
                for data,ins_list in datas.iteritems():
                    app_diff['dynamic_data'][name][data] = "%d instances, like [%s]" % \
                            (len(ins_list), ','.join(ins_list[0:1]))
        if len(app_diff['package_data_source']) == 0:
            del app_diff['package_data_source']
        if len(app_diff['static_data']) == 0:
            del app_diff['static_data']
        if len(app_diff['dynamic_data']) == 0:
            del app_diff['dynamic_data']
        if len(app_diff) > 0:
            diff[app_id] = app_diff
    
    outfile = "/home/work/data/%s/%s.instance.diff.%s" % (stat_time, cluster, module)
    fout = open(outfile, 'w')
    print >>fout, json.dumps(diff, sort_keys=True, indent=2)

