import sys
import json

stat_time = sys.argv[1]
cluster = sys.argv[2]

infile = "/home/work/data/%s/%s.instance.dump" % (stat_time, cluster)
listfile = "/home/work/data/%s/%s.instance.list" % (stat_time, cluster)
datafile = "/home/work/data/%s/%s.instance.data" % (stat_time, cluster)

fin = file(infile)
flist = open(listfile, 'w')
fdata = open(datafile, 'w')

s = json.load(fin)

#instance.list
for k,v in s['sons'].iteritems():
    if k == 'global':
        continue
    app_id = k
    app_meta = v['meta']
    ins_map = v['sons']
    if 'package' in app_meta and 'module_name' in app_meta['package']:
        module = app_meta['package']['module_name']
        if app_id.startswith("testenv"):
            module = "testenv"
    else:
        module = 'null'
    for k1,v1 in ins_map.iteritems():
        if k1 == 'tags' or k1 == 'control_node':
            continue
        ins_id = k1
        ins_meta = v1['meta']
        ins_sons = v1['sons']
        if 'hostname' in ins_meta:
            hostname = ins_meta['hostname']
        else:
            hostname = 'null'
        if 'begin_port' in ins_meta:
            begin_port = str(ins_meta['begin_port'])
        else:
            begin_port = 'null'
        if 'work_path' in ins_meta:
            work_path = ins_meta['work_path']
        else:
            work_path = 'null'
        run_state = 'null'
        if 'status' in ins_sons:
            ins_status = ins_sons['status']['meta']
            if 'runtime' in ins_status:
                ins_runtime = ins_status['runtime']
                if 'run_state' in ins_runtime:
                    run_state = ins_runtime['run_state']
        print >>flist, "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
                ins_id, module, app_id, hostname, run_state, work_path, begin_port)
flist.close()

#instance.data
apps = {}
for k,v in s['sons'].iteritems():
    if k == 'global':
        continue
    app_id = k
    app = {}
    apps[app_id] = app
    app_meta = v['meta']
    ins_map = v['sons']
    if 'package' in app_meta and 'module_name' in app_meta['package']:
        module = app_meta['package']['module_name']
        if app_id.startswith("testenv"):
            module = "testenv"
    else:
        module = 'null'
    app['module'] = module
    inss = {}
    app['instances'] = inss
    for k1,v1 in ins_map.iteritems():
        if k1 == 'tags' or 'control_node':
            continue
        ins = {}
        inss[k1] = ins
        ins_meta = v1['meta']
        ins_sons = v1['sons']
        ins['hostname'] = 'null'
        if 'hostname' in ins_meta:
            ins['hostname'] = ins_meta['hostname']
        dynamics = {}
        statics = {}
        ins['dynamic_data'] = dynamics
        ins['static_data'] = statics
        ins['package_data_source'] = 'null'
        ins['run_state'] = 'null'
        if 'status' in ins_sons:
            ins_status = ins_sons['status']['meta']
            if 'dynamic_data' in ins_status:
                for k2,v2 in ins_status['dynamic_data']['items'].iteritems():
                    dynamic = {}
                    dynamic['data_source'] = v2['data_source']
                    dynamic['timestamp'] = 'null'
                    if 'timestamp' in v2:
                        dynamic['timestamp'] = v2['timestamp']
                    dynamics[k2] = dynamic
            if 'package' in ins_status:
                ins['package_data_source'] = ins_status['package']['data_source']
                if 'static_data' in ins_status['package']:
                    for k2,v2 in ins_status['package']['static_data']['items'].iteritems():
                        static = {}
                        static['data_source'] = v2['data_source']
                        static['timestamp'] = 'null';
                        if 'timestamp' in v2:
                            static['timestamp'] = v2['timestamp']
                        statics[k2] = static
            if 'runtime' in ins_status:
                ins_runtime = ins_status['runtime']
                if 'run_state' in ins_runtime:
                    ins['run_state'] = ins_runtime['run_state']
print >>fdata, json.dumps(apps, sort_keys=True, indent=2)
fdata.close()
