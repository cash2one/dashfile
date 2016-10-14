#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys
import json


def main():
    all = sys.argv[1]
    ip_json = sys.argv[2]
    instid = sys.argv[3]
    appid = sys.argv[4]

    outfile1 = "./package_date_source.tmp"
    outfile2 = "./ltr_ranksvm_model_chn.tmp"
    outfile3 = "./base_bs.tmp"

    fout1 = open(outfile1, 'a')
    fout2 = open(outfile2, 'a')
    fout3 = open(outfile3, 'a')

    try:
        o = json.loads(all)
    except Exception, e:
        print e,"err:",instid,appid
        return

    package_data_source = o["package"]["data_source"]
    if package_data_source == "":
        package_data_source = "EMPTY"
    status = o["state"]
    ip_o = json.loads(ip_json)
    ip = ip_o["hostname"]

    items_d = o["dynamic_data"]["items"]
    ltr_data_source = "NO_LTR_RANKSVM_MODEL_CHN"
    if "ltr_ranksvm_model_chn" in items_d:
        timestamp = items_d["ltr_ranksvm_model_chn"].get("timestamp","NO_TIMESTAMP")
        if timestamp == "":
            timestamp = "EMPTY"
        ltr_data_source = items_d["ltr_ranksvm_model_chn"].get("data_source","NO_DATA_SOURCE")
        if ltr_data_source == "":
            ltr_data_source = "EMPTY"

        ltr_data_source = "(%s)%s" % (timestamp,ltr_data_source)

    items_s = o["package"]["static_data"]["items"]
    base_bs_data_source = "NO_BASE_BS"
    if "base_bs" in items_s:
        base_bs_data_source = items_s["base_bs"].get("data_source","NO_DATA_SOURCE")
        if base_bs_data_source == "":
            base_bs_data_source = "EMPTY"

    print >> fout1, "%s %s %s %s %s" % (appid,instid,status,ip,package_data_source)
    print >> fout2, "%s %s %s %s %s" % (appid,instid,status,ip,ltr_data_source)
    print >> fout3, "%s %s %s %s %s" % (appid,instid,status,ip,base_bs_data_source)

if __name__ == '__main__':
    main()
