#!/usr/bin/env bash

CURRDIR=`dirname "$0"`
# 当前目录
BASEDIR=`cd ${CURRDIR}; pwd`

PROJECT_DIR=`cd ${BASEDIR}/..;pwd`
CONFIG_DIR=${PROJECT_DIR}/config


echo "------------------------- 开始初始化python虚拟环境 -------------------------"
# 初始化python环境
cd ${PROJECT_DIR}
# 创建虚拟环境
python3 -m venv venv
sleep 1
# 激活venv
source 'venv/bin/activate'
# 安装python3依赖库
${PROJECT_DIR}/venv/bin/pip3 install -r requirements.txt
echo "------------------------- 成功初始化python虚拟环境 -------------------------"


echo -e '\n\n\n'

echo "------------------------- 开始初始化mysql数据库 -------------------------"
# 初始化数据库
cd ${CONFIG_DIR}
echo 'Mysql host:'
read host
echo -e 'Mysql user:'
read user
echo -e 'Mysql password:'
read password
mysql -h ${host} -u ${user} -p"${password}" < mirror.sql
echo "------------------------- 成功初始化mysql数据库 -------------------------"
