#!/bin/sh
stat_time=`date +%y%m%d`
curh=`date "+%H"`
if [ $curh = "03" ]
then
    mkdir -p /home/work/data_zk_consistent/$stat_time
    get_snapshot.sh > /home/work/zk_log/snapshot.log 2>&1
    ./check.sh > /home/work/zk_log/check.log 2>&1
    ./zk_show.sh > /home/work/zk_log/zk_show.log 2>&1
fi

rm -f /home/work/data_zk_consistent/latest

ln -s /home/work/data_zk_consistent/$stat_time /home/work/data_zk_consistent/latest
