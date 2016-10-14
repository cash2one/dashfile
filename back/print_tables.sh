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

echo "������ʹ���ʡ�${br}"
echo "{{Ӳ����}} : level-1���ϻ��� + ����ά�޵Ļ��� + ��ɾ���Ļ���${br}"
echo "{{�����}} : ��Ӳ���� && ( agent==unavail || ( agent==avail && �ѷ���ʵ�� && ��ʵ������running״̬ ) )${br}"
echo "{{�޹���}} : ��Ӳ���� && agent==avail && ( δ����ʵ�� || ( �ѷ���ʵ�� && ���ٴ���һ��ʵ������running״̬ ) )${br}"
echo "{{��ʹ��}} : agent==avail && �ѷ���ʵ�� && ���ٴ���һ��ʵ������running״̬${br}"
echo "���online�� = ���Ϊonline�Ļ����� / �ܻ�����${br}"
echo "Ӳ������ = Ӳ���ϻ����� / �ܻ�����${br}"
echo "������� = ����ϻ����� / �ܻ�����${br}"
echo "�޹����� = �޹��ϻ����� / �ܻ�����${br}"
echo "�޹��ϻ���ʹ���� = ��ʹ�õ��޹��ϻ����� / �޹��ϻ�����${br}"
echo "��ʹ���� = ��ʹ�õĻ����� / �ܻ�����${br}"
echo "��Ⱥ	������ǩ	�ܻ�����	���online��	Ӳ������	�������	�޹�����	�޹��ϻ���ʹ����	��ʹ����" >$tmp_file
cat /home/work/data/${stat_time}/machine.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

echo "��Agent����ʡ�${br}"
echo "�ܴ���� = ״̬Ϊavailable��agent�� / �ܻ�����${br}"
echo "��Ӳ���ϻ�������� = ��Ӳ���ϻ�����״̬Ϊavailable��agent�� / ��Ӳ���ϻ�����${br}"
echo "��Ⱥ	�ܻ�����	�ܴ����	��Ӳ���ϻ�����	��Ӳ���ϻ��������" >$tmp_file
cat /home/work/data/${stat_time}/agent.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

echo "��ʵ������ʡ�${br}"
echo "{{basa}} : ����acģ��${br}"
echo "{{*core*}} : ['basa','bc','bs','disp','attr','dictserver']${br}"
echo "{{ʵ����������}} : agent==avail && ʵ����״̬Ϊrunning${br}"
echo "ʵ������� = ����������ʵ���� / ��ʵ����${br}"
echo "��Ⱥ	ģ��	��ʵ����	ʵ�������	Naming��ʵ����	Naming��ʵ�������" >$tmp_file
cat /home/work/data/${stat_time}/instance.table >>$tmp_file
python $format_tool $tmp_file
if [ $? -ne 0 ]
then
    exit 1
fi
echo "${br}"

rm $tmp_file

