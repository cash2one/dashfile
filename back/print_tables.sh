#!/bin/sh

stat_time=$1
format_type=$2

tmp_file=/home/work/data/${stat_time}.print.table.tmp
if [ "$format_type" = "html" ]
then
    br="<br>"
    format_tool="format_table_html.py"
else
    br=""
    format_tool="format_table_text.py"
fi

echo "【机器使用率】${br}"
echo "{{硬故障}} : level-1故障机器 + 正在维修的机器 + 已删除的机器${br}"
echo "{{软故障}} : 非硬故障 && ( agent==unavail || ( agent==avail && 已分配实例 && 无实例处于running状态 ) )${br}"
echo "{{无故障}} : 非硬故障 && agent==avail && ( 未分配实例 || ( 已分配实例 && 至少存在一个实例处于running状态 ) )${br}"
echo "{{被使用}} : agent==avail && 已分配实例 && 至少存在一个实例处于running状态${br}"
echo "标记online率 = 标记为online的机器数 / 总机器数${br}"
echo "硬故障率 = 硬故障机器数 / 总机器数${br}"
echo "软故障率 = 软故障机器数 / 总机器数${br}"
echo "无故障率 = 无故障机器数 / 总机器数${br}"
echo "无故障机器使用率 = 被使用的无故障机器数 / 无故障机器数${br}"
echo "总使用率 = 被使用的机器数 / 总机器数${br}"
echo "集群	机器标签	总机器数	标记online率	硬故障率	软故障率	无故障率	无故障机器使用率	总使用率" >$tmp_file
cat /home/work/data/${stat_time}/machine.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

echo "【Agent存活率】${br}"
echo "总存活率 = 状态为available的agent数 / 总机器数${br}"
echo "非硬故障机器存活率 = 非硬故障机器上状态为available的agent数 / 非硬故障机器数${br}"
echo "集群	总机器数	总存活率	非硬故障机器数	非硬故障机器存活率" >$tmp_file
cat /home/work/data/${stat_time}/agent.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

echo "【实例存活率】${br}"
echo "{{basa}} : 就是ac模块${br}"
echo "{{*core*}} : ['basa','bc','bs','disp','attr','dictserver']${br}"
echo "{{实例运行正常}} : agent==avail && 实例的状态为running${br}"
echo "实例存活率 = 运行正常的实例数 / 总实例数${br}"
echo "集群	模块	总实例数	实例存活率	Naming中实例数	Naming中实例存活率" >$tmp_file
cat /home/work/data/${stat_time}/instance.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

rm $tmp_file

