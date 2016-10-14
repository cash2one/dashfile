#!/bin/sh

stat_time=$1
mypath=/home/work/dashboard/back/wangshuai14

echo "WANGSHUAI[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] BEGIN"

python ${mypath}/yj_machine.py $stat_time
if [ $? -ne 0 ]
then
    exit 1
fi

sh ${mypath}/insert_tables.sh $stat_time
if [ $? -ne 0 ]
then 
    exit 1
fi

mkdir -p /home/work/data_lv2/${stat_time}
python ${mypath}/gen_machien_tree.py $stat_time 

rm -f /home/work/data_lv2/latest
ln -s /home/work/data_lv2/$stat_time /home/work/data_lv2/latest

sh ${mypath}/fault_sort.sh
sh ${mypath}/fault_sort_ns.sh
sh ${mypath}/machine_label_add.sh
python ${mypath}/machine_label.py
sh ${mypath}/machine_label_insert_table.sh
sh ${mypath}/get_unused_machine.sh
python ${mypath}/get_ins_cluster.py
python ${mypath}/get_mac_cluster.py
sh /home/work/dashboard/back/wangshuai14/insertdb.sh
sh /home/work/dashboard/back/wangshuai14/machine_analysis/bin/routine_stat.sh
sh /home/work/dashboard/back/wangshuai14/insertmac.sh

echo "WANGSHUAI[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] END"

