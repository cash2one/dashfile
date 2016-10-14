#!/bin/bash

stat_time=$1
cluster=$2

infile="/home/work/data/${stat_time}/${cluster}.machine.list"
outfile="/home/work/data/${stat_time}/${cluster}.agent.list"

thread=100

mkfifo ff
exec 4<>ff 
unlink ff

>$outfile

for((i=0;i<$thread;i++))
{
    echo >&4;
}

for i in `awk '{print $1}' $infile`
do
    (bash get_agent_state.sh $cluster $i >>$outfile; echo >&4) &
    read <&4 
done

