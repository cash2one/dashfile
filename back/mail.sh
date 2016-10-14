#!/bin/sh

stat_time=$1

mail_from=wanggang15@baidu.com
mail_to=beehive@baidu.com
result_html=/home/work/data/${stat_time}/result.html

sh print_tables.sh $stat_time html >$result_html
if [ $? -ne 0 ]
then
    exit 1
fi

cat $result_html | formail -I "From: $mail_from" -I"To: $mail_to" -I "MIME-Version:1.0" -I "Content-type:text/html;charset=gb2312" -I "Subject: Beehive Statistics at 20${stat_time}:00" | /usr/sbin/sendmail -oi $mail_to

