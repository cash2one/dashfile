#!/bin/bash

stat_time=$1
cluster=$2

python remove_garbage.py $stat_time $cluster
python stat_machine_health_raw.py $stat_time $cluster
if [ $? -ne 0 ]
then
    exit 1
fi

infile="/home/work/data/${stat_time}/${cluster}.machine_health_raw.list"
outfile="/home/work/data/${stat_time}/${cluster}.machine_health.list"

thread=100

mkfifo ff
exec 4<>ff 
unlink ff

>$outfile

for((i=0;i<$thread;i++))
{
    echo >&4;
}

while read line
do
    (
    hostname=`echo $line | cut -d" " -f1`
    err=`echo $line | cut -d" " -f2`
    ip=`host -i $hostname | grep "has address" | cut -d" " -f4`
    if [ -z "$ip" ]
    then
        ip="null"
    fi
    echo "$hostname	$ip	$err" >>$outfile
    echo >&4
    ) &
    read <&4 
done <$infile

wait
