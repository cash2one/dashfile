#!/bin/sh

if [ -f ./version_info ]
then
    rm ./version_info
fi

while read line
do
    cluster=`echo $line | cut -d' ' -f1`
    host=`echo $line | cut -d' ' -f2`

    version_shell=`ssh wanggang15@$host "/home/work/beehive/shell/bin/bh_daemon --version" < /dev/null | head -1 | awk '{print $2}' | awk -F'_' '{print $2}' | awk -F'.' '{print $3}'` 
    version_pd=`ssh wanggang15@$host "/home/work/beehive/pd/bin/pd --version" < /dev/null | head -1 | awk '{print $2}' | awk -F'_' '{print $2}' | awk -F'.' '{print $3}'` 
    version_rm=`ssh wanggang15@$host "/home/work/beehive/rm/bin/rm --version" < /dev/null | head -1 | awk '{print $2}' | awk -F'_' '{print $2}' | awk -F'.' '{print $3}'` 
    echo "$cluster shell $version_shell" >> ./version_info
    echo "$cluster pd $version_pd" >> ./version_info
    echo "$cluster rm $version_rm" >> ./version_info

done < ./main.list
