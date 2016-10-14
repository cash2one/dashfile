#!/bin/sh

stat_time=$1
data_root=/home/work

echo "[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] BEGIN"
mkdir -p $data_root/data/${stat_time}

while read line
do
    cluster=`echo $line | cut -d' ' -f1`
    zk_host=`echo $line | cut -d' ' -f2`
    echo "[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] [$cluster] BEGIN"

    wget ${zk_host}:/home/work/opbin/zk_dump/data/dump/lastest.slavenode \
        -O $data_root/data/${stat_time}/${cluster}.machine.dump --tries=2 &>/dev/null
    if [ $? -ne 0 -o ! -s "$data_root/data/${stat_time}/${cluster}.machine.dump" ]
    then
        cp $data_root/data_backup/${cluster}.machine.dump $data_root/data/${stat_time}/${cluster}.machine.dump &>/dev/null
        echo "error:wget $cluster.machine.dump use data of old"
        echo ${cluster}.machine.dump err ${usable_date} >> $data_root/data/${stat_time}/history 
    else
        cp $data_root/data/${stat_time}/${cluster}.machine.dump $data_root/data_backup/${cluster}.machine.dump &>/dev/null
        echo ${cluster}.machine.dump ok ${stat_time} >> $data_root/data/${stat_time}/history 
    fi

    wget ${zk_host}:/home/work/opbin/zk_dump/data/dump/lastest.service-instance \
        -O $data_root/data/${stat_time}/${cluster}.instance.dump --tries=2 &>/dev/null
    if [ $? -ne 0 -o ! -s "$data_root/data/${stat_time}/${cluster}.instance.dump" ]
    then
        cp $data_root/data_backup/${cluster}.instance.dump $data_root/data/${stat_time}/${cluster}.instance.dump &>/dev/null
        echo "error:wget $cluster.instance.dump use data of old"
        echo ${cluster}.instance.dump err ${usable_date} >> $data_root/data/${stat_time}/history 
    else
        cp $data_root/data/${stat_time}/${cluster}.instance.dump $data_root/data_backup/${cluster}.instance.dump &>/dev/null
        echo ${cluster}.instance.dump ok ${stat_time} >> $data_root/data/${stat_time}/history 
    fi

    wget ${zk_host}:/home/work/opbin/zk_dump/data/dump/lastest.naming \
        -O $data_root/data/${stat_time}/${cluster}.naming.dump --tries=2 &>/dev/null
    if [ $? -ne 0 -o ! -s "$data_root/data/${stat_time}/${cluster}.naming.dump" ]
    then
        cp $data_root/data_backup/${cluster}.naming.dump $data_root/data/${stat_time}/${cluster}.naming.dump &>/dev/null
        echo "error:wget $cluster.naming.dump use data of old"
        echo ${cluster}.naming.dump err ${usable_date} >> $data_root/data/${stat_time}/history 
    else
        cp $data_root/data/${stat_time}/${cluster}.naming.dump $data_root/data_backup/${cluster}.naming.dump &>/dev/null
        echo ${cluster}.naming.dump ok ${stat_time} >> $data_root/data/${stat_time}/history 
    fi

    echo "begin of dump allretbeehive_${cluster}"
    wget nj02-www-maclife.nj02.baidu.com:/home/work/tools/auto_repair/data/allretbeehive_${cluster} \
        -O $data_root/data/${stat_time}/${cluster}.machine_health.dump --tries=2 &>/dev/null
    if [ $? -ne 0 -o ! -s "$data_root/data/${stat_time}/${cluster}.machine_health.dump" ]
    then
        cp $data_root/data_backup/${cluster}.machine_health.dump $data_root/data/${stat_time}/${cluster}.machine_health.dump &>/dev/null
        echo "error:wget $cluster.machine_health.dump use data of old"
        echo ${cluster}.machine_health.dump err ${usable_date} >> $data_root/data/${stat_time}/history 
    else
        cp $data_root/data/${stat_time}/${cluster}.machine_health.dump $data_root/data_backup/${cluster}.machine_health.dump &>/dev/null
        echo ${cluster}.machine_health.dump ok ${stat_time} >> $data_root/data/${stat_time}/history 
    fi
    echo "end of dump allretbeehive_${cluster}"

    python stat_machine.py $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "python stat_machine.py $stat_time $cluster"
        exit 1
    fi
    sh stat_machine_health.sh $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "sh stat_machine_health.sh $stat_time $cluster"
        exit 1
    fi
    python stat_machine_err.py $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "python stat_machine_err.py $stat_time $cluster"
        exit 1
    fi
    python stat_instance.py $stat_time $cluster succ
    if [ $? -ne 0 ]
    then
        echo "BEGIN get instance.dump from 155 "
        python stat_instance.py $stat_time ${cluster} fail
        if [ $? -ne 0 ]
        then
            exit 1
        fi
        echo "END get instance.dump from 155 "
    else
        cp $data_root/data/${stat_time}/${cluster}.instance.dump $data_root/data_bu/${cluster}.instance.dump
    fi
    sh stat_agent.sh $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "sh stat_agent.sh $stat_time $cluster"
        exit 1
    fi
    python gen_instance_diff.py $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "python gen_instance_diff.py $stat_time $cluster"
        exit 1
    fi
    python stat_naming_raw.py $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "python stat_naming_raw.py $stat_time $cluster"
        exit 1
    fi
    python stat_naming.py $stat_time $cluster
    if [ $? -ne 0 ]
    then
        echo "python stat_naming.py $stat_time $cluster"
        exit 1
    fi
    echo "[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] [$cluster] END"
done <./vice.list

sh gen_tables.sh $stat_time
if [ $? -ne 0 ]
then
    echo "sh gen_tables.sh $stat_time"
    exit 1
fi

sh insert_tables.sh $stat_time
if [ $? -ne 0 ]
then
    echo "sh insert_tables.sh $stat_time"
    exit 1
fi

result=$data_root/data/${stat_time}/result
sh print_tables.sh $stat_time text >$result
if [ $? -ne 0 ]
then
    exit 1
fi

rm $data_root/data/${stat_time}/*.machine.dump \
   $data_root/data/${stat_time}/*.instance.dump \
   $data_root/data/${stat_time}/*.instance.data \
   $data_root/data/${stat_time}/*.naming.dump

echo "[$stat_time] [`date "+%Y-%m-%d %H:%M:%S"`] END"

