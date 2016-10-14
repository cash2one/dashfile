#!/bin/sh
stat_time=`date +%y%m%d`
path=/home/work/data_zk_consistent/$stat_time

while read line
do
    cluster=`echo $line | cut -d' ' -f1`

    ./get_err_app_show_header.py $path/${cluster}_base_bs > $path/${cluster}_base_bs_header
    ./get_err_app_show_header.py $path/${cluster}_ltr_ranksvm_model_chn > $path/${cluster}_ltr_ranksvm_model_chn_header
    ./get_err_app_show_header.py $path/${cluster}_package_date_source > $path/${cluster}_package_date_source_header

    ./get_err_app_better_format.py $path/${cluster}_base_bs > $path/${cluster}_base_bs_tmp
    ./get_err_app_better_format.py $path/${cluster}_ltr_ranksvm_model_chn > $path/${cluster}_ltr_ranksvm_model_chn_tmp
    ./get_err_app_better_format.py $path/${cluster}_package_date_source > $path/${cluster}_package_date_source_tmp

    python ./get_err.py $path/${cluster}_base_bs > $path/${cluster}_base_bs_err
    python ./get_err.py $path/${cluster}_ltr_ranksvm_model_chn > $path/${cluster}_ltr_ranksvm_model_chn_err
    python ./get_err.py $path/${cluster}_package_date_source > $path/${cluster}_package_date_source_err

    python ./get_err_app_show_body_jstree.py $path/${cluster}_base_bs_tmp $path/${cluster}_base_bs_err > $path/${cluster}_base_bs_body_jstree
    python ./get_err_app_show_body_jstree.py $path/${cluster}_ltr_ranksvm_model_chn_tmp $path/${cluster}_ltr_ranksvm_model_chn_err > $path/${cluster}_ltr_ranksvm_model_chn_body_jstree
    python ./get_err_app_show_body_jstree.py $path/${cluster}_package_date_source_tmp $path/${cluster}_package_date_source_err > $path/${cluster}_package_date_source_body_jstree

    #./get_err_app_show_body.py $path/${cluster}_base_bs_tmp > $path/${cluster}_base_bs_body
    #./get_err_app_show_body.py $path/${cluster}_ltr_ranksvm_model_chn_tmp > $path/${cluster}_ltr_ranksvm_model_chn_body
    #./get_err_app_show_body.py $path/${cluster}_package_date_source_tmp > $path/${cluster}_package_date_source_body

    #./get_err_app_show_body_txt_.py $path/${cluster}_base_bs_tmp > $path/${cluster}_base_bs_body_txt
    #./get_err_app_show_body_txt_.py $path/${cluster}_ltr_ranksvm_model_chn_tmp > $path/${cluster}_ltr_ranksvm_model_chn_body_txt
    #./get_err_app_show_body_txt_.py $path/${cluster}_package_date_source_tmp > $path/${cluster}_package_date_source_body_txt

done < ./zk.list



