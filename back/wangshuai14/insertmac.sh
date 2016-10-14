#!/bin/bash

logfile=/home/work/dashboard/back/wangshuai14/insertmac.log
month=`date +%m`
day=`date +%d`
hour=`date +%H`

python /home/work/dashboard/back/wangshuai14/insertmac.py $month $day $hour >> $logfile 2>&1
