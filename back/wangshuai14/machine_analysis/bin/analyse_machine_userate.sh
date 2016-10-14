#!/usr/bin/env bash

set -o pipefail

RM_DUMP_FILE=""
PD_DUMP_FILE=""
NS_DUMP_FILE=""
ALLRET_FILE=""
CLUSTER_NAME=""
SHELL_DUMP_FILE=""
EXTRA_CONF_FILE=""

function print_usage()
{
    echo "Usage: `basename $0` [r:p:n:e:c:]"
    echo "    -r rm dump file"
    echo "    -p pd dump file"
    echo "    -n ns dump file"
    echo "    -s shell dump file"
    echo "    -e err machine list"
    echo "    -c cluster name"
    echo "    -f extra conf finle"
}

while getopts 'r:p:n:s:e:c:f:' opt
do
    case ${opt} in
        r)
            RM_DUMP_FILE=${OPTARG}
            ;;
        p)
            PD_DUMP_FILE=${OPTARG}
            ;;
        n)
            NS_DUMP_FILE=${OPTARG}
            ;;
        s)
            SHELL_DUMP_FILE=${OPTARG}
            ;;
        e)
            ALLRET_FILE=${OPTARG}
            ;;
        c)
            CLUSTER_NAME=${OPTARG}
            ;;
        f)
            EXTRA_CONF_FILE=${OPTARG}
            ;;
        ?)
            print_usage
            exit 1
    esac
done

if [ "x${RM_DUMP_FILE}" == "x" ]
then
    echo "rm dump file is must"
    print_usage
    exit 1
fi

if [ "x${PD_DUMP_FILE}" == "x" ]
then
    echo "pd dump file is must"
    print_usage
    exit 1
fi

# ns is not a must now

if [ "x${ALLRET_FILE}" == "x" ]
then
    echo "err machine list file(allretbeehive) is must"
    print_usage
    exit 1
fi

if [ "x${CLUSTER_NAME}" == "x" ]
then
    CLUSTER_NAME="unkown_cluster"
fi

if [ "x${EXTRA_CONF_FILE}" == "x" ]
then
    echo "extra conf file is a must"
    print_usage
    exit 1
fi

RESULT_FILE_NAME=${CLUSTER_NAME}.analyse_machine_userate.result

function append_to_result_file
{
    level=$1
    info=$2

    append_mode="append"
    if [ $# -eq 3 ]
    then
        append_mode=$3
    fi

    prefix_str="| ---- "
    if [ ${level} == 0 ]
    then
        prefix_str=""
    else
        for ((j = 1; j < ${level}; j++))
        do
            prefix_str="|\t"${prefix_str}
        done
    fi

    info=${prefix_str}${info}
    
    if [ "x${append_mode}" == "xinit" ]
    then
        echo -e ${info} > ${RESULT_FILE_NAME}
    else
        echo -e ${info} >> ${RESULT_FILE_NAME}
    fi
}

function analyse_err_class
{
    ERR_TYPE_ENUM=("ERR_MACHINE_UNREACHABLE" \
    "ERR_HOME_DISK_IO" \
    "ERR_SSD_IO" \
    "ERR_SSD_PARAM" \
    "ERR_SSD_DROP" \
    "ERR_HOME_DROP" \
    "ERR_FILE_IO" \
    "ERR_IN_ERROR_POOL" \
    "ERR_MEMORY" \
    "ERR_SOFT_ENV" \
    "ERR_HANDLING_NOW" \
    "ERR_UNSPECIFIED" \
    "ERR_UNKNOWN")

    err_file=$1

    for err_class in ${ERR_TYPE_ENUM[@]}
    do
        analyse_expresion="/.*/ERR_CLASS.MATCH.${err_class}"

        err_class_num=`analyse_json.py -i ${err_file} -e"${analyse_expresion}" | stat_json.py -mcount -p/.*`
        if [ ${err_class_num} -ne 0 ]
        then
            append_to_result_file 3 "${err_class_num} = ${err_class} (file: ${err_file})"
        fi
    done
}

# 1 �������������ʹ����
# 1.1 ��ȡȫ��������״̬,���� state,label,heartbeat,availability ����
extract_zkdump_batch_value.py -i ${RM_DUMP_FILE} -p/machine/.*\..* -k/state,/label --path_1=/machine/.*\..*/control_node --keys_1=/heartbeat,/availability --path_2=/machine/.*\..*/.*_[0-9]*$ --keys_2=/container_group_id -okv > ${CLUSTER_NAME}.machine.all
if [ $? -ne 0 ]
then
    echo 'extract rm zkdump failed'
    exit 1
fi

#### temp, ��ʱȥ�� wise-bs �ڵ� ####
analyse_json.py -i ${CLUSTER_NAME}.machine.all -mor -e"/machine/.*/label.CONTAIN.wise-bs,/machine/.*/label.CONTAIN.wise-abc" > ${CLUSTER_NAME}.machine.wise-bs
op_json.py --f1=${CLUSTER_NAME}.machine.all --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.wise-bs --p2=/machine > ${CLUSTER_NAME}.machine

# 1.2 ��ȡ heartbeat Ϊ available ״̬�Ļ����б�
analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/control_node/heartbeat.MATCH.available" > ${CLUSTER_NAME}.machine.available
if [ $? -ne 0 ]
then
    echo 'extract available machine failed'
    exit 1
fi

# 1.3 ��ȡȫ�� app ��ȫ�� instance ״̬,������ instance ���ڻ����� hostname,�Լ��� instance �� run_state
extract_zkdump_batch_value.py -i ${PD_DUMP_FILE} -p/.*/.*_[0-9]*$ -k/hostname --path_1=/.*/.*_[0-9]*$/status --keys_1=/runtime/run_state --path_2=/.*/control_node/usable --keys_2=/shared_num -okv > ${CLUSTER_NAME}.service.state
if [ $? -ne 0 ]
then
    echo 'extract pd zkdump failed'
    exit 1
fi

# 1.4 ��ȡ run_state Ϊ RUNNING �� instance �б�,�����Ӧ�� app
analyse_json.py -i ${CLUSTER_NAME}.service.state -e"/.*/.*/status/runtime/run_state.MATCH.RUNNING" > ${CLUSTER_NAME}.service.instance.RUNNING
if [ $? -ne 0 ]
then
    echo 'extract running instance failed'
    exit 1
fi

# 1.5 ���˳����ٴ���һ�� RUNNING ʵ���� app �б�,����Ӧ����Щ����ʵ���Լ���Ӧ������ hostname 
op_json.py --f1=${CLUSTER_NAME}.service.state --p1=/.* -minclude_filter --f2=${CLUSTER_NAME}.service.instance.RUNNING --p2=/.* > ${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING
if [ $? -ne 0 ]
then
    echo 'extract app list with at least one running instance failed'
    exit 1
fi

# 1.6 �� available �Ļ����б�ȫ����,���˳��û�����������һ�����ʵ��,��״̬Ϊ RUNNING �Ļ����б�
op_json.py --f1=${CLUSTER_NAME}.machine.available --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING --p2=/.*/.*/hostname > ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING
if [ $? -ne 0 ]
then
    echo 'extract machine list with at least one running instance failed'
    exit 1
fi

# 1.7 �������ʹ����
machine_total_num=`stat_json.py -i ${CLUSTER_NAME}.machine -mcount -p/machine/.*`
machine_used_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING -mcount -p/machine/.*`
machine_unused_num=`echo ${machine_total_num}-${machine_used_num} | bc`
machine_userate=`echo ${machine_used_num}/${machine_total_num}*100 | bc -l`
machine_userate=`printf "%.2f" ${machine_userate}`

# 1.8 ���ʹ���ʷ������
append_to_result_file 0 "------------------------------------------------" "init"
append_to_result_file 0 "analyse result from CLUSTER=${CLUSTER_NAME} RM=${RM_DUMP_FILE}, PD=${PD_DUMP_FILE}, NS=${NS_DUMP_FILE}, ERR_MACHINE=${ALLRET_FILE} EXTRA_CONF_FILE=${EXTRA_CONF_FILE}"
append_to_result_file 0 "------------------------------------------------"
append_to_result_file 0 ""
append_to_result_file 0 "|--- USERATE SUMMARISE ---"
append_to_result_file 0 "| ${machine_total_num} = machine_total_num (file: ${CLUSTER_NAME}.machine)"
append_to_result_file 0 "| ${machine_used_num} = machine_used_num (file: ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING)"
append_to_result_file 0 "| ${machine_userate}% = machine_userate"
append_to_result_file 0 "|-------------------------"

# 2 ��ʼ����δ����ʹ�õĻ�����ԭ���б�
append_to_result_file 0 ""
append_to_result_file 0 "|--- ANALYSE OF UNUSED MACHINES ---"
append_to_result_file 0 "| ${machine_unused_num} = machine_unused_num"

# 2.1 ��ȡ heartbeat Ϊ unavailable ״̬�Ļ����б�
analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/control_node/heartbeat.NOT_MATCH.available" > ${CLUSTER_NAME}.machine.unavailable
if [ $? -ne 0 ]
then
    echo 'extract unavailable machine list failed'
    exit 1
fi
machine_unavailable_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable -mcount -p/machine/.*`
append_to_result_file 1 "${machine_unavailable_num} = machine_unavailable_num (file: ${CLUSTER_NAME}.machine.unavailable)"

# ��Ԭ�������� beehive ԭʼ hostname ������,��������ӳ��ת�����Բ���Ҫ
## 2.2 ��ȡ���ϻ����б�(allretbeehive.list),�����˳����ǹ��ĵ����ع���
#extract_allretbeehive.py -i ${ALLRET_FILE} -mgethostname -pfix_mac,handling > ${CLUSTER_NAME}.allretbeehive.list
## ���������һЩӳ�������,�Ѿ���Ԭ����ԭʼ�б�������� beehive ԭʼ�� hostname ��
## ���ɴӻ������� beehive �ڲ� hostname ��ӳ���
#if [ ! -f allret2beehive_hostname.map ]
#then
#    extract_json.py -i ${CLUSTER_NAME}.machine -p/machine -k | generate_allret2beehive_hostname_map.py > allret2beehive_hostname.map
#fi
## �� bj.allretbeehive.list ����Ļ�����ת���� beehive �ڲ��� hostname
#cat ${CLUSTER_NAME}.allretbeehive.list | allret2beehive_hostname_trans.py > ${CLUSTER_NAME}.allretbeehive.list.beehive

# 2.2 ��ȡ���ϻ����б�(allretbeehive.list.beehive)
extract_allretbeehive.py -i ${ALLRET_FILE} -mget_beehive_hostname -pfix_mac,handling,handling_onser,some_ser_err,lv2cetus,root_passwd -r"ANY,ANY,ANY,ANY,ANY,ANY" > ${CLUSTER_NAME}.allretbeehive.list.beehive
if [ $? -ne 0 ]
then
    echo 'extract err machine list from allret_beehive failed'
    exit 1
fi

# 2.3 ���������б�
# 2.3.1 һ���� machine.unavailable �� allretbeehive.list �Ľ���,����б����еĻ���,��Ӧ�ñ����û���״̬Ϊ offline
# ��Щ����,�������(�����ǿ��ö�)��Ҫ����ά��,��Ϊ�����ϵķ������Ѿ����������ṩ������,�ٿ��ǿ��ö�û������
op_json.py --f1=${CLUSTER_NAME}.machine.unavailable --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr
if [ $? -ne 0 ]
then
    echo 'extract machine list which is unavailable and in err list failed'
    exit 1
fi
machine_unavailabel_inerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable.inerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_unavailabel_inerr_num} = inerr_num (file: ${CLUSTER_NAME}.machine.unavailable.inerr)"

# 2.3.1.1 ���ֹ�������
extract_allretbeehive.py -i ${ALLRET_FILE} -mparse_reason -l ${CLUSTER_NAME}.allretbeehive.list.beehive > ${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS
if [ $? -ne 0 ]
then
    echo 'parse err reason from err machine list failed'
    exit 1
fi

op_json.py --f1=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --p1=/ -minclude_filter --f2=${CLUSTER_NAME}.machine.unavailable.inerr --p2=/machine > ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS
if [ $? -ne 0 ]
then
    echo 'get err reason from unavailable machine list failed'
    exit 1
fi

# ������������,����ӡ�����Ϣ
analyse_err_class ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS

# 2.3.2 ��һ���� machine.unavailable �� allretbeehive.list �Ĳ
# ����б�,��Ҫ������ϸ����Ϊ����Щ�������ڹ��ϻ����б�����,���� agent ״̬ȴ�� unavailable
# ���ֿ���,һ�������ǵ� agent ��ĳЩ������� bug û����������,��һ���� allretbeehive ���ϻ�������ٻز�����ȱ��
op_json.py --f1=${CLUSTER_NAME}.machine.unavailable --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.unavailable.NOTinerr
if [ $? -ne 0 ]
then
    echo 'get machine list which is unavailable but not in err list failed'
    exit 1
fi
machine_unavailabel_NOTinerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable.NOTinerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_unavailabel_NOTinerr_num} = NOTinerr_num (file: ${CLUSTER_NAME}.machine.unavailable.NOTinerr)"

# 2.3.3 ���� 2.3.2 �б����еĻ���,��Ҫ���ݿ��ö��Լ���ʵ��ԭ��,�����Ƿ���Ҫ��������ά�޻��߲������������ָ� agent

# 2.4 ��ȡ���� heartbeat ״̬ available,���ǻ�����û���κ�һ�� RUNNING ״̬ʵ���Ļ����б�
op_json.py --f1=${CLUSTER_NAME}.machine.available --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING --p2=/.*/.*/hostname > ${CLUSTER_NAME}.machine.available.NO_RUNNING
if [ $? -ne 0 ]
then
    echo 'get machine list which is available but no running instance failed'
    exit 1
fi
machine_available_but_no_running_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING -mcount -p/machine/.*`
append_to_result_file 1 "${machine_available_but_no_running_num} = machine_available_but_no_running_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING)"

# 2.4 ���������б�
# 2.4.1 һ���� machine.available.NO_RUNNING �� allretbeehive.list �Ľ���
# ��Щ����,��������ֱ�����߽���ά��,��Ϊ�������Ѿ�û��ʵ��,�����ڹ����б���
# ����Ҫ��һ��,Ϊʲô����������,������ agent ��״̬���� available ��
# (��Ȼ,�����п��ܵ�,ֻ�ǿ���������״̬�㱨���ܲ����н�һ���Ĳ���,������Դ�������Ч��)
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr
if [ $? -ne 0 ]
then
    echo 'get machine list which is available and no running instance and in err list failed'
    exit 1
fi
machine_availabel_but_no_running_inerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_availabel_but_no_running_inerr_num} = inerr_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr)"

# 2.4.1.1 ���ֹ�������
op_json.py --f1=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --p1=/ -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS
if [ $? -ne 0 ]
then
    echo '[2.4.1.1 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --p1=/ -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS'
    exit 1
fi

# ������������,����ӡ�����Ϣ
analyse_err_class ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS

# 2.4.2 ��һ���� machine.available.NO_RUNNING �� allretbeehive.list �Ĳ
# ��Щ������Ҫ����һ��Ϊ��û�б���ȷʹ������
# ������֮ǰ���ֵĻ���ά�޻���֮��, agent �����Զ����� stop ��ʵ��
# Ҳ��������������,��Ҫ�������
# anyway,��Щ����,�������������Զ�Ǩ��ʱ,�������õĻ����ն���Դ
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr
if [ $? -ne 0 ]
then
    echo '[2.4.2 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr'
    exit 1
fi
machine_availabel_but_no_running_NOTinerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_availabel_but_no_running_NOTinerr_num} = NOTinerr_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr)"

# ����û�� RUNNING ʵ��,���ֲ��ڹ��ϻ����б��������Щ�������������
# ��������Ļ������ܺ�,Ӧ�õ��� machine_availabel_but_no_running_NOTinerr_num
# 2.4.2.1 �Ȳ�������Щ���������Ӧ�� container ���
op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info
if [ $? -ne 0 ]
then
    echo '[2.4.2.1 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info'
    exit 1
fi

# 2.4.2.2 ���ȿ�һ��,��Щ��������,��Щ������û�з����κ�ʵ����
analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.NOT_HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER
if [ $? -ne 0 ]
then
    echo '[2.4.2.2 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.NOT_HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER'
fi

NO_CONTAINER_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER -mcount -p/machine/.*`
append_to_result_file 3 "${NO_CONTAINER_num} = NO_CONTAINER_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER)"

# 2.4.2.3 ������������ container ����Щ�������б�,���ҽ�ʵ��������״̬join����. ����б�Ӧ���� 2.4.2.4/5/6/7 ��ȫ��
analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER
if [ $? -ne 0 ]
then
    echo '[2.4.2.3 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER'
    exit 1
fi
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER --p1=/machine/.* -mjoin --f2=${CLUSTER_NAME}.service.state --p2=/.* > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info
if [ $? -ne 0 ]
then
    echo '[2.4.2.3 step FAILED] -> p_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER --p1=/machine/.* -mjoin --f2=${CLUSTER_NAME}.service.state--p2=/.* > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info'
    exit 1
fi

HAS_CONTAINER_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER -mcount -p/machine/.*`
append_to_result_file 3 "${HAS_CONTAINER_num} = HAS_CONTAINER_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER)"

# 2.4.2.4 Ȼ��һ��,��Щ��Щ������ʵ���Ļ�����,����Щ�����ϵ�ʵ������ STOP ״̬��
analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info -e"/machine/.*/.*_[0-9]*$/status/runtime/run_state.MATCH.STOP" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.4 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info -e"/machine/.*/.*_[0-9]*$/status/runtime/run_state.MATCH.STOP" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE'
    exit 1
fi

analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info -e"/machine/.*/.*_[0-9]*$/status/runtime/run_state.NOT_MATCH.STOP" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.4 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info -e"/machine/.*/.*_[0-9]*$/status/runtime/run_state.NOT_MATCH.STOP" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE'
    exit 1
fi

op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.4 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE'
    exit 1
fi

ONLY_HAS_STOP_INSTANCE_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE -mcount -p/machine/.*`
append_to_result_file 4 "${ONLY_HAS_STOP_INSTANCE_num} = ONLY_HAS_STOP_INSTANCE_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE)"

# 2.4.2.5 Ȼ���ٲ�����Щ�����ϵ�ʵ�����Ƿ� STOP ״̬��(���� NEW,REPAIR,DEPLOYFAIL ��)
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.5 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE'
    exit 1
fi

ONLY_HAS_NOT_STOP_INSTANCE_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE  -mcount -p/machine/.*`
append_to_result_file 4 "${ONLY_HAS_NOT_STOP_INSTANCE_num} = ONLY_HAS_NOT_STOP_INSTANCE_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE)"

# 2.4.2.6 ��Щ������,���� STOP ״̬��ʵ��,���з� STOP ״̬��ʵ��
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE.tmp
if [ $? -ne 0 ]
then
    echo '[2.4.2.6 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE.tmp'
    exit 1
fi

op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE.tmp --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.6 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.with_instance_info --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE.tmp --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE'
    exit 1
fi
rm -f ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE.tmp

HAS_STOP_AND_NOT_STOP_INSTANCE_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE  -mcount -p/machine/.*`
append_to_result_file 4 "${HAS_STOP_AND_NOT_STOP_INSTANCE_num} = HAS_STOP_AND_NOT_STOP_INSTANCE_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE)"

# 2.4.2.7 ��Щ������,�� RM ��������� container ,������ PD ��û���κ�ʵ��
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER --p1=/machine/.* -mexlude_filter --f2=${CLUSTER_NAME}.service.state --p2=/.* > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE.tmp
if [ $? -ne 0 ]
then
    echo '[2.4.2.7 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER --p1=/machine/.* -mexlude_filter --f2=${CLUSTER_NAME}.service.state --p2=/.* > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE.tmp'
    exit 1
fi

analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE.tmp -manalyse_keys -e"/machine/.*.HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.7 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE.tmp -manalyse_keys -e"/machine/.*.HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE'
    exit 1
fi
rm -f ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE.tmp

op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp
if [ $? -ne 0 ]
then
    echo '[2.4.2.7 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.NO_PD_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp'
    exit 1
fi

op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp1
if [ $? -ne 0 ]
then
    echo '[2.4.2.7 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_AND_NOT_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp1'
    exit 1
fi

op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp1 --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.7 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp1 --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE'
    exit 1
fi

rm -f ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp
rm -f ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE.tmp1

ONLY_HAS_NO_PD_INSTANCE_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE -mcount -p/machine/.*`
append_to_result_file 4 "${ONLY_HAS_NO_PD_INSTANCE_num} = ONLY_HAS_NO_PD_INSTANCE_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_CONTAINER.ONLY_HAS_NO_PD_INSTANCE)"
append_to_result_file 0 "|----------------------------------"

function note(){
    # 3 ������ά�޻����б�
    # 3.1 �������д�ά�޻����ĺ�ѡȫ����Ӧ�� container ��Ϣ,������Ӧ�Ĺ��������б��� join
    op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container.tmp
    if [ $? -ne 0 ]
    then
        echo '[step 3.1 FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container.tmp'
        exit 1
    fi

    op_json.py --f1=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container.tmp --p1=/machine -mjoin --f2=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container
    if [ $? -ne 0 ]
    then
        echo '[step 3.1 FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container.tmp --p1=/machine -mjoin --f2=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container'
        exit 1
    fi
    rm -f ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container.tmp

    op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container.tmp
    if [ $? -ne 0 ]
    then
        echo 'op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container.tmp'
        exit 1
    fi

    op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container.tmp --p1=/machine -mjoin --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container
    if [ $? -ne 0 ]
    then
        echo '[step 3.1 FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container.tmp --p1=/machine -mjoin --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container'
        exit 1
    fi
    rm -f ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container.tmp

    # 3.2 ����������Щ������Ӧ�� container ��Ӧ�� app �Ŀ��ö���Ϣ
    extract_zkdump_batch_value.py -i ${PD_DUMP_FILE} -p/.*/control_node/usable/.* > ${CLUSTER_NAME}.service.usable.instance
    if [ $? -ne 0 ]
    then
        echo '[3.2 step FAILED] -> extract_zkdump_batch_value.py -i ${PD_DUMP_FILE} -p/.*/control_node/usable > ${CLUSTER_NAME}.service.usable.instance'
        exit 1
    fi

    op_json.py --f1=${CLUSTER_NAME}.service.usable.instance --p1=/.*/control_node -mjoin --f2=${CLUSTER_NAME}.service.state --p2=/.*/control_node > ${CLUSTER_NAME}.service.usable.tmp
    if [ $? -ne 0 ]
    then
        echo '[3.2 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.service.usable.instance --p1=/.*/control_node -mjoin --f2=${CLUSTER_NAME}.service.state --p2=/.*/control_node > ${CLUSTER_NAME}.service.usable.tmp'
        exit 1
    fi

    op_json.py --f1=${CLUSTER_NAME}.service.state --p1=/ -mjoin --f2=${CLUSTER_NAME}.service.usable.tmp --p2=/ > ${CLUSTER_NAME}.service.usable
    if [ $? -ne 0 ]
    then
        echo '[3.2 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.service.state --p1=/ -mjoin --f2=${CLUSTER_NAME}.service.usable.tmp --p2=/ > ${CLUSTER_NAME}.service.usable'
        exit 1
    fi
    rm -f ${CLUSTER_NAME}.service.usable.tmp

    # 3.3 ����������Ϣ,ɸѡ��������ά�޵Ļ����б�
    # ������ά�޻����б�,��Ҫ��ȡ��ά��ȫ�ֻ���ά��״̬
    source ${EXTRA_CONF_FILE}

    GLOBAL_MACHINE_FIXING_STATE_DIR=${GLOBAL_MACHINE_FIXING_STATE_DIR}/`date +%F`
    if [ ! -d ${GLOBAL_MACHINE_FIXING_STATE_DIR} ]
    then
        mkdir -p ${GLOBAL_MACHINE_FIXING_STATE_DIR}
    fi
    LATEST_GLOBAL_MACHINE_FIXING_STATE_FILE=${GLOBAL_MACHINE_FIXING_STATE_DIR}/../${CLUSTER_NAME}.${GLOBAL_MACHINE_FIXING_STATE_FILE_NAME}.latest
    GLOBAL_MACHINE_FIXING_STATE_FILE_NAME=${GLOBAL_MACHINE_FIXING_STATE_DIR}/${CLUSTER_NAME}.${GLOBAL_MACHINE_FIXING_STATE_FILE_NAME}.`date +%H-%M`

    extract_allretbeehive.py -i ${ALLRET_FILE} -mget_beehive_hostname -pall_ok -r"ANY" > ${CLUSTER_NAME}.allret_ok.list.beehive
    if [ $? -ne 0 ]
    then
        echo '[get all_ok list from allret file failed]'
        exit 1
    fi

    if [ "x${FIX_MACHINE_GENERATOR_CONF}" != "x" ]
    then
        FIX_MACHINE_GENERATOR_CONF="--config=${FIX_MACHINE_GENERATOR_CONF}"
    fi

    fix_machine_generator.py ${FIX_MACHINE_GENERATOR_CONF} --unavailable=${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS.container --no_running=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS.container --usable=${CLUSTER_NAME}.service.usable --total_machine_list=${CLUSTER_NAME}.machine --allret_ok=${CLUSTER_NAME}.allret_ok.list.beehive --latest_fix_state=${LATEST_GLOBAL_MACHINE_FIXING_STATE_FILE} --new_fix_state=${GLOBAL_MACHINE_FIXING_STATE_FILE_NAME} --allret_err=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS > ${CLUSTER_NAME}.machine.tofix.list
    if [ $? -ne 0 ]
    then
        echo '[generate fix machine list failed]'
        exit 1
    else
        # �����µĻ���ȫ��״̬�������ļ�����
        ln -sf ${GLOBAL_MACHINE_FIXING_STATE_FILE_NAME} ${LATEST_GLOBAL_MACHINE_FIXING_STATE_FILE}
    fi


    # 3.4 ������ʷ������״̬,�Լ���ǰ���������Ĺ��ϻ����ֲ����ά���б�
    # �ֱ���� tosetonline �Լ� tosetoffline �б�

    # 3.4.1 �Ȳ�����ǰ�Ļ���״̬�б�
    analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/state.MATCH.online" > ${CLUSTER_NAME}.machine.online
    if [ $? -ne 0 ]
    then
        echo '[get online machine list failed]'
        exit 1
    fi

    analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/state.MATCH.offline" > ${CLUSTER_NAME}.machine.offline
    if [ $? -ne 0 ]
    then
        echo '[get offline machine list failed]'
        exit 1
    fi

    if [ "x${MACHINE_STATE_GENERATOR_CONF}" != "x" ]
    then
        MACHINE_STATE_GENERATOR_CONF="--config=${MACHINE_STATE_GENERATOR_CONF}"
    fi

    # 3.4.2 ���� online �б�,������,��ǰ״̬�� offline,���ǹ��ϼ��Ľ���Ѿ���ok��
    machine_state_generator.py ${MACHINE_STATE_GENERATOR_CONF} -mgen_online --cur_offline=${CLUSTER_NAME}.machine.offline --allret_ok=${CLUSTER_NAME}.allret_ok.list.beehive > ${CLUSTER_NAME}.machine.tosetonline.list
    if [ $? -ne 0 ]
    then
        echo '[generate online machine list failed]'
        exit 1
    fi

    # 3.4.3 ���� offline �б�,������,��ǰ״̬�� online,���ǻ������ض�����
    # ע��:������ offline �Ļ���,��һ���ڱ��� tofix �Ļ����б�����
    # ���������,�����Զ�ά���Լ��Զ�����״̬���õĽ���,�����ߵĲ��Խ��ԽС
    machine_state_generator.py -mgen_offline ${MACHINE_STATE_GENERATOR_CONF} --cur_online=${CLUSTER_NAME}.machine.online --allret_err=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --total_machine_num=${machine_total_num} > ${CLUSTER_NAME}.machine.tosetoffline.list
    if [ $? -ne 0 ]
    then
        echo '[generate offline machine list failed]'
        exit 1
    fi

    # ���ò�����������
    if [ "x${LATEST_OUTPUT_DIR}" != "x" ]
    then
        ln -sf `readlink -f ${RESULT_FILE_NAME}` ${LATEST_OUTPUT_DIR}/${RESULT_FILE_NAME}.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tofix.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tofix.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.should_fix_ever_before.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.should_fix_ever_before.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tosetonline.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tosetonline.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tosetoffline.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tosetoffline.list.latest
    fi
}