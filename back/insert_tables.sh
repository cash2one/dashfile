#!/bin/sh

stat_time=$1

types="machine agent instance"

for type in $types
do
    table_name=stat_${type}
    table_file=`readlink -f /home/work/data/${stat_time}/${type}.table.sql`
    echo "load data local infile \"${table_file}\" into table ${table_name};" | mysql -u root newdb
    if [ $? -ne 0 ]
    then
        exit 1
    fi
done

