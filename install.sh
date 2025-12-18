#!/bin/bash

# 项目启动脚本（Linux）
# 用法：将此脚本保存为 run_project.sh，放在项目根目录，然后执行：
#   chmod +x run_project.sh
#   ./run_project.sh

set -e  # 遇到错误立即退出

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"

echo "=================================="
echo "酒店产品管理系统 启动脚本"
echo "项目目录: ${PROJECT_DIR}"
echo "=================================="

# 1. 创建虚拟环境（如果不存在）
if [ ! -d "${VENV_DIR}" ]; then
    echo "未检测到虚拟环境，正在创建..."
    python3 -m venv "${VENV_DIR}"
    echo "虚拟环境创建完成: ${VENV_DIR}"
else
    echo "检测到已有虚拟环境: ${VENV_DIR}"
fi

# 2. 激活虚拟环境
echo "正在激活虚拟环境..."
source "${VENV_DIR}/bin/activate"

# 3. 严格检查是否真的激活成功
if [[ "$VIRTUAL_ENV" != "${VENV_DIR}" ]]; then
    echo "错误：虚拟环境激活失败！"
    echo "当前 VIRTUAL_ENV: $VIRTUAL_ENV"
    echo "预期路径: ${VENV_DIR}"
    exit 1
fi

echo "虚拟环境已成功激活（$(python --version)）"

# 4. 检查并安装依赖
echo "正在检查并安装依赖..."
pip install --quiet --upgrade pip

# 需要的包列表
REQUIRED_PACKAGES="flask flask-login werkzeug"

for pkg in $REQUIRED_PACKAGES; do
    if ! pip show "$pkg" > /dev/null 2>&1; then
        echo "正在安装 $pkg ..."
        pip install --quiet "$pkg"
    else
        echo "$pkg 已安装"
    fi
done

# 5. 创建必要目录
UPLOADS_DIR="${PROJECT_DIR}/static/uploads"
if [ ! -d "${UPLOADS_DIR}" ]; then
    echo "创建图片上传目录: ${UPLOADS_DIR}"
    mkdir -p "${UPLOADS_DIR}"
else
    echo "图片上传目录已存在"
fi

# 6. 运行项目
echo "=================================="
echo "所有准备就绪，正在启动 Flask 项目..."
echo "访问地址：http://127.0.0.1:5000"
echo "按 Ctrl+C 停止服务"
echo "=================================="

python app.py