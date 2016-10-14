#!/bin/sh

cluster=$1
machine=$2

if [ "$cluster" = "beijing" ]
then
    zk_server="10.23.30.47:2181,10.42.59.15:2181,10.42.60.16:2181,10.36.130.64:2181,10.38.106.43:2181"
elif [ "$cluster" = "hangzhou" ]
then
    zk_server="10.212.212.54:2181,10.212.213.44:2181,10.212.214.12:2181,10.211.47.19:2181,10.211.23.38:2181"
elif [ "$cluster" = "nanjing" ]
then
    zk_server="10.207.49.44:2181,10.207.54.44:2181,10.207.47.44:2181,10.207.46.44:2181,10.207.53.44:2181"
elif [ "$cluster" = "shanghai" ]
then
    zk_server="10.202.212.49:2181,10.202.219.52:2181,10.202.245.23:2181,10.202.254.31:2181,10.202.245.21:2181"
elif [ "$cluster" = "tucheng" ]
then
    zk_server="10.46.185.36:2181,10.46.186.15:2181,10.92.28.16:2181,10.42.208.21:2181,10.23.14.23:2181"
else
    echo "$machine	null"
    exit 1
fi

state=`zkcli node get --server=$zk_server --path=/beehive/rm/machine/${machine}/control_node --pretty 2>/dev/null \
    | grep heartbeat | cut -d'"' -f4`

if [ -z "x$state" ]
then
    state="null"
fi

if [ "$state" = "unavailable" -o "$state" = "null" ]
then
    unified_state="unavail"
else
    unified_state="avail"
fi

echo "$machine	$state	$unified_state"

