#!/bin/sh
curr_hour=`date +%H`
get_date=`date +%Y-%m-%d`
get_hour="02-00"
if [ $curr_hour = "04" ]
then 
    mkdir -p /home/work/data_unused_machine/$get_date/$get_hour
    cd /home/work/data_unused_machine/$get_date/$get_hour
    wget -r --no-directories yf-pa-bsvip255-0-j2-off.yf01.baidu.com:/home/work/cenketie/routine_stat/analyse_machine_userate/$get_date/$get_hour   &>/dev/null
    cd ../../
    rm -f latest
    ln -s ./$get_date latest
fi    
