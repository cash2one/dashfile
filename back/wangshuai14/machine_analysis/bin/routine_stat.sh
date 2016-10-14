#!/usr/bin/env bash

# crontab 定期统计分析脚本
# 每天分析3次,分别是 2:00,10:00,18:00
# (对应的 zkdump 数据备份时间是 1:00,9:00,17:00)

# 创建当前的数据目录
stat_dir=/home/work/data_unused_machine/data

if [ ! -d ${stat_dir} ];then
    mkdir -p ${stat_dir}
fi

# 需要执行的分析列表
stat_list=("analyse_machine_userate")
stat_script_dir=/home/work/dashboard/back/wangshuai14/machine_analysis/bin

export PATH=${PATH}:${stat_script_dir}

# 需要分析的 zkdump 的数据位置
zkdump_source_dir=/home/work/dashboard/back/wangshuai14/machine_analysis/input_data
rm_dump_name_suffix=slavenode.zkdump.latest
pd_dump_name_suffix=service-instance.zkdump.latest
ns_dump_name_suffix=naming.zkdump.latest

# allretbeehive 的位置
allretbeehive_dir=/home/work/dashboard/back/wangshuai14/machine_analysis/input_data
allretbeehive_name_prefix=allretbeehive
# 主要服务单元分布
service_units_num=5
service_units=("sh" "tc" "nj" "hz" "bj")
service_units_fullspel=("shanghai" "tucheng" "nanjing" "hangzhou" "beijing")
today=`date +%F`
cur_time=`date +%H`

# 开始分析
for one_stat in ${stat_list[@]}
do
    dest_dir=${stat_dir}/${one_stat}/${today}/${cur_time}
    if [ ! -d ${dest_dir} ];then
        mkdir -p ${dest_dir}
    fi
    log_file=${stat_dir}/../log/${one_stat}.log.${today}-${cur_time}
    cd ${dest_dir}

    stat_script_dir=`readlink -f ${stat_script_dir}/${one_stat}.sh`
    stat_script_dir=`dirname ${stat_script_dir}`
    for ((i = 0; i < ${service_units_num}; i++))
    do
        rm_dump_file=`readlink -f ${zkdump_source_dir}/${service_units[$i]}.${rm_dump_name_suffix}`
        pd_dump_file=`readlink -f ${zkdump_source_dir}/${service_units[$i]}.${pd_dump_name_suffix}`
        ns_dump_file=`readlink -f ${zkdump_source_dir}/${service_units[$i]}.${ns_dump_name_suffix}`
        allretbeehive_file=`readlink -f ${allretbeehive_dir}/${allretbeehive_name_prefix}_${service_units_fullspel[$i]}.latest`

        sh -x ${stat_script_dir}/${one_stat}.sh -r ${rm_dump_file} -p ${pd_dump_file} -n ${ns_dump_file} -e ${allretbeehive_file} -c ${service_units[$i]} -f ${stat_script_dir}/../conf/${one_stat}.conf 2>${log_file}
    done
done

