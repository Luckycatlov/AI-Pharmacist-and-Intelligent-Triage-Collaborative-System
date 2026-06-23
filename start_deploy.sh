#!/bin/bash

echo "============================================================"
echo "    医疗问答系统 - 本地部署脚本"
echo "============================================================"

# 检查Python版本
python --version || { echo "错误: Python未安装"; exit 1; }

# 检查必要的文件
if [ ! -f "deploy.py" ]; then
    echo "错误: 找不到deploy.py文件"
    exit 1
fi

# 安装依赖
echo "[1/3] 检查依赖..."
pip install -q -r requirements.txt || { echo "错误: 依赖安装失败"; exit 1; }

# 检查模型
echo "[2/3] 检查模型文件..."
if [ ! -d "models/text2vec-base-chinese" ]; then
    echo "警告: 中文嵌入模型不存在，请先运行: python setup_model.py"
    echo "是否继续？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        exit 1
    fi
fi

# 启动服务
echo "[3/3] 启动API服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "按Ctrl+C停止服务"
echo ""

python deploy.py