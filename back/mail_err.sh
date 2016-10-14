#!/bin/sh

stat_time=$1

mail_from=wanggang15@baidu.com
mail_to1=wanggang15@baidu.com
mail_to2=wangshuai14@baidu.com
log_file=/home/work/data/${stat_time}/log

cat $log_file | sed 's/$/<br>/' | formail -I "From: $mail_from" -I"To: $mail_to1" -I "MIME-Version:1.0" -I "Content-type:text/html;charset=gb2312" -I "Subject: [WARNING] Beehive Statistics Failed for [${stat_time}]" | /usr/sbin/sendmail -oi $mail_to1
cat $log_file | sed 's/$/<br>/' | formail -I "From: $mail_from" -I"To: $mail_to2" -I "MIME-Version:1.0" -I "Content-type:text/html;charset=gb2312" -I "Subject: [WARNING] Beehive Statistics Failed for [${stat_time}]" | /usr/sbin/sendmail -oi $mail_to2

