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

# 1 分析并计算机器使用率
# 1.1 获取全量机器的状态,包括 state,label,heartbeat,availability 几项
extract_zkdump_batch_value.py -i ${RM_DUMP_FILE} -p/machine/.*\..* -k/state,/label --path_1=/machine/.*\..*/control_node --keys_1=/heartbeat,/availability --path_2=/machine/.*\..*/.*_[0-9]*$ --keys_2=/container_group_id -okv > ${CLUSTER_NAME}.machine.all
if [ $? -ne 0 ]
then
    echo 'extract rm zkdump failed'
    exit 1
fi

#### temp, 临时去掉 wise-bs 节点 ####
analyse_json.py -i ${CLUSTER_NAME}.machine.all -mor -e"/machine/.*/label.CONTAIN.wise-bs,/machine/.*/label.CONTAIN.wise-abc" > ${CLUSTER_NAME}.machine.wise-bs
op_json.py --f1=${CLUSTER_NAME}.machine.all --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.wise-bs --p2=/machine > ${CLUSTER_NAME}.machine

# 1.2 获取 heartbeat 为 available 状态的机器列表
analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/control_node/heartbeat.MATCH.available" > ${CLUSTER_NAME}.machine.available
if [ $? -ne 0 ]
then
    echo 'extract available machine failed'
    exit 1
fi

# 1.3 获取全量 app 的全量 instance 状态,包括该 instance 所在机器的 hostname,以及该 instance 的 run_state
extract_zkdump_batch_value.py -i ${PD_DUMP_FILE} -p/.*/.*_[0-9]*$ -k/hostname --path_1=/.*/.*_[0-9]*$/status --keys_1=/runtime/run_state --path_2=/.*/control_node/usable --keys_2=/shared_num -okv > ${CLUSTER_NAME}.service.state
if [ $? -ne 0 ]
then
    echo 'extract pd zkdump failed'
    exit 1
fi

# 1.4 获取 run_state 为 RUNNING 的 instance 列表,及其对应的 app
analyse_json.py -i ${CLUSTER_NAME}.service.state -e"/.*/.*/status/runtime/run_state.MATCH.RUNNING" > ${CLUSTER_NAME}.service.instance.RUNNING
if [ $? -ne 0 ]
then
    echo 'extract running instance failed'
    exit 1
fi

# 1.5 过滤出至少存在一个 RUNNING 实例的 app 列表,及相应的那些存活的实例以及对应机器的 hostname 
op_json.py --f1=${CLUSTER_NAME}.service.state --p1=/.* -minclude_filter --f2=${CLUSTER_NAME}.service.instance.RUNNING --p2=/.* > ${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING
if [ $? -ne 0 ]
then
    echo 'extract app list with at least one running instance failed'
    exit 1
fi

# 1.6 从 available 的机器列表全集中,过滤出该机器上至少有一个存活实例,且状态为 RUNNING 的机器列表
op_json.py --f1=${CLUSTER_NAME}.machine.available --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING --p2=/.*/.*/hostname > ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING
if [ $? -ne 0 ]
then
    echo 'extract machine list with at least one running instance failed'
    exit 1
fi

# 1.7 计算机器使用率
machine_total_num=`stat_json.py -i ${CLUSTER_NAME}.machine -mcount -p/machine/.*`
machine_used_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING -mcount -p/machine/.*`
machine_unused_num=`echo ${machine_total_num}-${machine_used_num} | bc`
machine_userate=`echo ${machine_used_num}/${machine_total_num}*100 | bc -l`
machine_userate=`printf "%.2f" ${machine_userate}`

# 1.8 输出使用率分析结果
append_to_result_file 0 "------------------------------------------------" "init"
append_to_result_file 0 "analyse result from CLUSTER=${CLUSTER_NAME} RM=${RM_DUMP_FILE}, PD=${PD_DUMP_FILE}, NS=${NS_DUMP_FILE}, ERR_MACHINE=${ALLRET_FILE} EXTRA_CONF_FILE=${EXTRA_CONF_FILE}"
append_to_result_file 0 "------------------------------------------------"
append_to_result_file 0 ""
append_to_result_file 0 "|--- USERATE SUMMARISE ---"
append_to_result_file 0 "| ${machine_total_num} = machine_total_num (file: ${CLUSTER_NAME}.machine)"
append_to_result_file 0 "| ${machine_used_num} = machine_used_num (file: ${CLUSTER_NAME}.machine.available.ATLEAST_1_RUNNING)"
append_to_result_file 0 "| ${machine_userate}% = machine_userate"
append_to_result_file 0 "|-------------------------"

# 2 开始分析未正常使用的机器的原因及列表
append_to_result_file 0 ""
append_to_result_file 0 "|--- ANALYSE OF UNUSED MACHINES ---"
append_to_result_file 0 "| ${machine_unused_num} = machine_unused_num"

# 2.1 获取 heartbeat 为 unavailable 状态的机器列表
analyse_json.py -i ${CLUSTER_NAME}.machine -e"/machine/.*/control_node/heartbeat.NOT_MATCH.available" > ${CLUSTER_NAME}.machine.unavailable
if [ $? -ne 0 ]
then
    echo 'extract unavailable machine list failed'
    exit 1
fi
machine_unavailable_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable -mcount -p/machine/.*`
append_to_result_file 1 "${machine_unavailable_num} = machine_unavailable_num (file: ${CLUSTER_NAME}.machine.unavailable)"

# 让袁嘉增加了 beehive 原始 hostname 的数据,所以以下映射转换可以不需要
## 2.2 获取故障机器列表(allretbeehive.list),仅过滤出我们关心的严重故障
#extract_allretbeehive.py -i ${ALLRET_FILE} -mgethostname -pfix_mac,handling > ${CLUSTER_NAME}.allretbeehive.list
## 这里额外做一些映射的事情,已经让袁嘉在原始列表里面产出 beehive 原始的 hostname 了
## 生成从机器名到 beehive 内部 hostname 的映射表
#if [ ! -f allret2beehive_hostname.map ]
#then
#    extract_json.py -i ${CLUSTER_NAME}.machine -p/machine -k | generate_allret2beehive_hostname_map.py > allret2beehive_hostname.map
#fi
## 将 bj.allretbeehive.list 里面的机器名转换成 beehive 内部的 hostname
#cat ${CLUSTER_NAME}.allretbeehive.list | allret2beehive_hostname_trans.py > ${CLUSTER_NAME}.allretbeehive.list.beehive

# 2.2 获取故障机器列表(allretbeehive.list.beehive)
extract_allretbeehive.py -i ${ALLRET_FILE} -mget_beehive_hostname -pfix_mac,handling,handling_onser,some_ser_err,lv2cetus,root_passwd -r"ANY,ANY,ANY,ANY,ANY,ANY" > ${CLUSTER_NAME}.allretbeehive.list.beehive
if [ $? -ne 0 ]
then
    echo 'extract err machine list from allret_beehive failed'
    exit 1
fi

# 2.3 产出两个列表
# 2.3.1 一个是 machine.unavailable 与 allretbeehive.list 的交集,这个列表当中的机器,都应该被设置机器状态为 offline
# 这些机器,如论如何(不考虑可用度)都要下线维修,因为机器上的服务本身已经不能正常提供服务了,再考虑可用度没有意义
op_json.py --f1=${CLUSTER_NAME}.machine.unavailable --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.unavailable.inerr
if [ $? -ne 0 ]
then
    echo 'extract machine list which is unavailable and in err list failed'
    exit 1
fi
machine_unavailabel_inerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable.inerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_unavailabel_inerr_num} = inerr_num (file: ${CLUSTER_NAME}.machine.unavailable.inerr)"

# 2.3.1.1 区分故障类型
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

# 分析故障类型,并打印相关信息
analyse_err_class ${CLUSTER_NAME}.machine.unavailable.inerr.with_ERR_CLASS

# 2.3.2 另一个是 machine.unavailable 与 allretbeehive.list 的差集
# 这个列表,需要线下详细分析为何这些机器不在故障机器列表里面,但是 agent 状态却是 unavailable
# 两种可能,一种是我们的 agent 在某些情况下有 bug 没有正常运行,另一种是 allretbeehive 故障机器检测召回策略有缺陷
op_json.py --f1=${CLUSTER_NAME}.machine.unavailable --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.unavailable.NOTinerr
if [ $? -ne 0 ]
then
    echo 'get machine list which is unavailable but not in err list failed'
    exit 1
fi
machine_unavailabel_NOTinerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.unavailable.NOTinerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_unavailabel_NOTinerr_num} = NOTinerr_num (file: ${CLUSTER_NAME}.machine.unavailable.NOTinerr)"

# 2.3.3 对于 2.3.2 列表当中的机器,需要根据可用度以及真实的原因,决定是否需要进行下线维修或者采用其他方法恢复 agent

# 2.4 获取机器 heartbeat 状态 available,但是机器上没有任何一个 RUNNING 状态实例的机器列表
op_json.py --f1=${CLUSTER_NAME}.machine.available --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.service.app.ATLEAST_1_RUNNING --p2=/.*/.*/hostname > ${CLUSTER_NAME}.machine.available.NO_RUNNING
if [ $? -ne 0 ]
then
    echo 'get machine list which is available but no running instance failed'
    exit 1
fi
machine_available_but_no_running_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING -mcount -p/machine/.*`
append_to_result_file 1 "${machine_available_but_no_running_num} = machine_available_but_no_running_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING)"

# 2.4 产出两个列表
# 2.4.1 一个是 machine.available.NO_RUNNING 与 allretbeehive.list 的交集
# 这些机器,本身可以直接下线进行维修,因为机器上已经没有实例,并且在故障列表里
# 但需要看一下,为什么机器故障了,但我们 agent 的状态还是 available 的
# (当然,这是有可能的,只是看看我们在状态汇报上能不能有进一步的策略,提升资源分配的有效性)
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr
if [ $? -ne 0 ]
then
    echo 'get machine list which is available and no running instance and in err list failed'
    exit 1
fi
machine_availabel_but_no_running_inerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_availabel_but_no_running_inerr_num} = inerr_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr)"

# 2.4.1.1 区分故障类型
op_json.py --f1=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --p1=/ -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS
if [ $? -ne 0 ]
then
    echo '[2.4.1.1 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --p1=/ -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS'
    exit 1
fi

# 分析故障类型,并打印相关信息
analyse_err_class ${CLUSTER_NAME}.machine.available.NO_RUNNING.inerr.with_ERR_CLASS

# 2.4.2 另一个是 machine.available.NO_RUNNING 与 allretbeehive.list 的差集
# 这些机器需要分析一下为何没有被正确使用起来
# 可能是之前发现的机器维修回来之后, agent 不会自动拉起 stop 的实例
# 也可能是其他问题,需要具体分析
# anyway,这些机器,可能是我们做自动迁移时,可以利用的机器空洞资源
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr
if [ $? -ne 0 ]
then
    echo '[2.4.2 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.allretbeehive.list.beehive --p2=/ > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr'
    exit 1
fi
machine_availabel_but_no_running_NOTinerr_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr -mcount -p/machine/.*`
append_to_result_file 2 "${machine_availabel_but_no_running_NOTinerr_num} = NOTinerr_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr)"

# 分析没有 RUNNING 实例,但又不在故障机器列表里面的那些机器的详情分类
# 以下四类的机器数总和,应该等于 machine_availabel_but_no_running_NOTinerr_num
# 2.4.2.1 先补充上这些机器里面对应的 container 情况
op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info
if [ $? -ne 0 ]
then
    echo '[2.4.2.1 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine --p1=/machine -minclude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info'
    exit 1
fi

# 2.4.2.2 首先看一下,这些机器里面,哪些机器是没有分配任何实例的
analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.NOT_HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER
if [ $? -ne 0 ]
then
    echo '[2.4.2.2 step FAILED] -> analyse_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.with_container_info -manalyse_keys -e"/machine/.*.NOT_HAS_CHILDREN..*_[0-9]*$" > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER'
fi

NO_CONTAINER_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER -mcount -p/machine/.*`
append_to_result_file 3 "${NO_CONTAINER_num} = NO_CONTAINER_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.NO_CONTAINER)"

# 2.4.2.3 产出机器上有 container 的那些机器的列表,并且将实例的运行状态join起来. 这个列表应该是 2.4.2.4/5/6/7 的全集
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

# 2.4.2.4 然后看一下,这些那些分配了实例的机器中,有哪些机器上的实例都是 STOP 状态的
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

# 2.4.2.5 然后再产出哪些机器上的实例都是非 STOP 状态的(包括 NEW,REPAIR,DEPLOYFAIL 等)
op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE
if [ $? -ne 0 ]
then
    echo '[2.4.2.5 step FAILED] -> op_json.py --f1=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_NOT_STOP_INSTANCE --p1=/machine -mexlude_filter --f2=${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.HAS_STOP_INSTANCE --p2=/machine > ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE'
    exit 1
fi

ONLY_HAS_NOT_STOP_INSTANCE_num=`stat_json.py -i ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE  -mcount -p/machine/.*`
append_to_result_file 4 "${ONLY_HAS_NOT_STOP_INSTANCE_num} = ONLY_HAS_NOT_STOP_INSTANCE_num (file: ${CLUSTER_NAME}.machine.available.NO_RUNNING.NOTinerr.ONLY_HAS_NOT_STOP_INSTANCE)"

# 2.4.2.6 哪些机器上,既有 STOP 状态的实例,又有非 STOP 状态的实例
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

# 2.4.2.7 哪些机器上,在 RM 里面分配了 container ,但是在 PD 上没有任何实例
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
    # 3 产出待维修机器列表
    # 3.1 产出所有待维修机器的候选全集对应的 container 信息,并与相应的故障类型列表做 join
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

    # 3.2 产出所有这些机器对应的 container 对应的 app 的可用度信息
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

    # 3.3 根据以上信息,筛选出可用于维修的机器列表
    # 产出可维修机器列表,需要读取并维护全局机器维修状态
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
        # 建立新的机器全局状态的最新文件软链
        ln -sf ${GLOBAL_MACHINE_FIXING_STATE_FILE_NAME} ${LATEST_GLOBAL_MACHINE_FIXING_STATE_FILE}
    fi


    # 3.4 根据历史机器的状态,以及当前分析出来的故障机器分布与待维修列表
    # 分别产出 tosetonline 以及 tosetoffline 列表

    # 3.4.1 先产出当前的机器状态列表
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

    # 3.4.2 产出 online 列表,条件是,当前状态是 offline,但是故障检测的结果已经是ok的
    machine_state_generator.py ${MACHINE_STATE_GENERATOR_CONF} -mgen_online --cur_offline=${CLUSTER_NAME}.machine.offline --allret_ok=${CLUSTER_NAME}.allret_ok.list.beehive > ${CLUSTER_NAME}.machine.tosetonline.list
    if [ $? -ne 0 ]
    then
        echo '[generate online machine list failed]'
        exit 1
    fi

    # 3.4.3 产出 offline 列表,条件是,当前状态是 online,但是机器有特定故障
    # 注意:被设置 offline 的机器,不一定在本次 tofix 的机器列表里面
    # 理想情况下,随着自动维修以及自动机器状态设置的进行,这两者的差集会越来越小
    machine_state_generator.py -mgen_offline ${MACHINE_STATE_GENERATOR_CONF} --cur_online=${CLUSTER_NAME}.machine.online --allret_err=${CLUSTER_NAME}.allretbeehive.list.beehive.with_ERR_CLASS --total_machine_num=${machine_total_num} > ${CLUSTER_NAME}.machine.tosetoffline.list
    if [ $? -ne 0 ]
    then
        echo '[generate offline machine list failed]'
        exit 1
    fi

    # 设置产出数据软链
    if [ "x${LATEST_OUTPUT_DIR}" != "x" ]
    then
        ln -sf `readlink -f ${RESULT_FILE_NAME}` ${LATEST_OUTPUT_DIR}/${RESULT_FILE_NAME}.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tofix.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tofix.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.should_fix_ever_before.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.should_fix_ever_before.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tosetonline.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tosetonline.list.latest
        ln -sf `readlink -f ${CLUSTER_NAME}.machine.tosetoffline.list` ${LATEST_OUTPUT_DIR}/${CLUSTER_NAME}.machine.tosetoffline.list.latest
    fi
}
