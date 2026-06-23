@echo off
echo ============================================================
echo     医疗问答系统 - 本地部署脚本
echo ============================================================

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装
    pause
    exit /b 1
)

REM 检查deploy.py
if not exist deploy.py (
    echo 错误: 找不到deploy.py文件
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 检查依赖...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

REM 检查模型
echo [2/3] 检查模型文件...
if not exist "models\text2vec-base-chinese" (
    echo 警告: 中文嵌入模型不存在，请先运行: python setup_model.py
    echo 是否继续？(y/n)
    set /p response=
    if not "%response%"=="y" exit /b 1
)

REM 启动服务
echo [3/3] 启动API服务...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 按Ctrl+C停止服务
echo.

python deploy.py

pause