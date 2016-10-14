#!/bin/sh
# zk数据一致性检查
. /home/work/.bashrc

root_latest=/home/work/data/latest

thread=5

mkfifo ff
exec 4<>ff 
unlink ff

for((i=0;i<$thread;i++))
{
    echo >&4;
}

while read line
do
    cluster=`echo $line | cut -d' ' -f1`
    host_port=`echo $line | cut -d' ' -f2`

    #if [ $cluster = "nanjing" ]
    #then
        apps=`l$cluster pd`
        for app in $apps
        do
            if [ $app != "global" -a ${app:0:7} != "testenv" -a ${app:0:2} = "bs" ]
            then
                insts=`l$cluster pd/$app`
                for inst in $insts
                do
                    if [ $inst != "tags" -a $inst != "control_node" ]
                    then
                        (
                        json_str=`g$cluster pd/$app/$inst/status`
                        json_ip=`g$cluster pd/$app/$inst`
                        python check.py "$json_str" "$json_ip" "$inst" "$app"
                        echo >&4
                        ) &
                        read <&4
                    fi
                done
            fi
        done
        wait

        python add_available.py $cluster > /home/work/zk_log/add_avai.log 2>&1

        rm ./package_date_source.tmp
        rm ./ltr_ranksvm_model_chn.tmp
        rm ./base_bs.tmp
    #fi
done < ./zk.list

