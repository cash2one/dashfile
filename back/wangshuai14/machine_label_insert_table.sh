#!/bin/sh

table_name=stat_machine_new
table_file=`readlink -f /home/work/data_ml/machine.table.sql`
echo "load data local infile \"${table_file}\" into table ${table_name};" | mysql -u root newdb

if [ $? -ne 0 ]
then
    exit 1
fi
