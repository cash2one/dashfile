#!/bin/bash

logfile=/home/work/dashboard/back/wangshuai14/insertdb.log
month=`date +%m`
day=`date +%d`
hour=`date +%H`

python /home/work/dashboard/back/wangshuai14/insertdb.py $month $day $hour >> $logfile 2>&1
