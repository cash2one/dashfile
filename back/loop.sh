#!/bin/sh

data_root=/home/work
dashboard_root=/home/work/dashboard/back

while :
do
    cur_hour=`date +%H`
    cur_minute=`date +%M`
    stat_time=`date +%y%m%d_%H`

    if [ "$cur_minute" != "00" ]
    then
        sleep 40
        continue
    fi

    echo "[$stat_time] BEGIN"
    mkdir -p $data_root/data/${stat_time}
    log_file=$data_root/data/${stat_time}/log

    sh get_version.sh

    sh stat.sh $stat_time >$log_file 2>&1
    if [ $? == 0 ]
    then
        stat_ret=succ
    else
        stat_ret=fail
    fi

    if [ "$stat_ret" = "succ" -a "$cur_hour" = "08" ]
    then
        sh mail.sh $stat_time >>$log_file 2>&1
        if [ $? == 0 ]
        then
            mail_ret=succ
        else
            mail_ret=fail
        fi
    fi

    if [ "$stat_ret" = "fail" -o "$mail_ret" = "fail" ]
    then
        sh mail_err.sh $stat_time
        echo "[$stat_time] FAIL"
    else
        cd $data_root/data
        rm -f latest
        ln -s $stat_time latest
        cd $dashboard_root
    fi
    
    if [ "$stat_ret" = "succ" -a "$cur_hour" = "01" ]
    then
        echo "kpi start" 
        python ./wangshuai14/kpi_machine.py
        python ./wangshuai14/kpi_instance.py
        echo "kpi end"
    fi

    echo "[$stat_time] END"

    #wanggang
    if [ "$stat_ret" = "succ" ]
    then
        ./consist.sh
    fi
    #wangshuai
    if [ "$stat_ret" = "succ" ]
    then
        sh ./wangshuai14/yj.sh $stat_time
    fi
    sleep 70
done


