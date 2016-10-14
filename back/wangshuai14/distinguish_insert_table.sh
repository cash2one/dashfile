#!/bin/sh

table_name=instance_fault
table_file=`readlink -f /home/work/data_if/instance_fault.sql`
echo "load data local infile \"${table_file}\" into table ${table_name};" | mysql -u root newdb
if [ $? -ne 0 ]
then
exit 1
fi

