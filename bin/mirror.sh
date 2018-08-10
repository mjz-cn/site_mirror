#!/usr/bin/env bash

CURRDIR=`dirname "$0"`
# 当前目录
BASEDIR=`cd ${CURRDIR}; pwd`

PROJECT_DIR=`cd ${BASEDIR}/..;pwd`

source "${PROJECT_DIR}/venv/bin/activate"

python_path=`which python3`

echo "Python路径: ${python_path}"

python3 "${PROJECT_DIR}/bin/mirror_bin.py" $@
