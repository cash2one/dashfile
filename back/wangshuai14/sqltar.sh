#!/bin/bash

cd /home/work/.jumbo/bin
mysqladmin -uroot shutdown
cd /home/work/.jumbo/var/lib
tar -zcvf /home/work/data_mysql/sqlbackup.tar.gz mysql 
cd /home/work/.jumbo/bin
mysqld_safe &
if [ $? -eq 0 ]
then 
    echo "mysqltar success"
else
    echo "mysqltar fail"
fi
