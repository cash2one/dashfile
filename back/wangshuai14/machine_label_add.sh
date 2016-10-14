#!/bin/sh
cat /home/work/data/latest/hangzhou.machine.list | awk '{ print $3}' | sort | uniq -c > /home/work/data_ml/hangzhou.machine_label\
.list

cat /home/work/data/latest/nanjing.machine.list | awk '{ print $3}' | sort | uniq -c > /home/work/data_ml/nanjing.machine_label\
.list

cat /home/work/data/latest/shanghai.machine.list | awk '{ print $3}' | sort | uniq -c > /home/work/data_ml/shanghai.machine_label\
.list

cat /home/work/data/latest/tucheng.machine.list | awk '{ print $3}' | sort | uniq -c > /home/work/data_ml/tucheng.machine_label\
.list

cat /home/work/data/latest/beijing.machine.list | awk '{ print $3}' | sort | uniq -c > /home/work/data_ml/beijing.machine_label\
.list


