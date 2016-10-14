#!/bin/sh

table_name=ns_total
table_file=`readlink -f /home/work/data_if/ns_total.sql`
echo "load data local infile \"${table_file}\" into table ${table_name};" | mysql -u root newdb
if [ $? -ne 0 ]
then
exit 1
fi

