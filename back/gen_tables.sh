#!/bin/sh

stat_time=$1

python gen_machine_table.py $stat_time
if [ $? -ne 0 ]
then
    exit 1
fi

python gen_agent_table.py $stat_time
if [ $? -ne 0 ]
then
    exit 1
fi

python gen_instance_table.py $stat_time
if [ $? -ne 0 ]
then
    exit 1
fi
