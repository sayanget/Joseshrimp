@echo off
setlocal
chcp 65001 > nul
title 销售管理系统启动器

echo ==========================================
echo       正在启动销售管理系统...
echo ==========================================

REM 切换到脚本所在目录，防止路径错误
cd /d "%~dp0"

REM 检查并激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] 使用虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] 未找到虚拟环境，使用系统默认Python...
)

REM 检查Python是否可用
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] 无法找到 Python！请确保已安装 Python。
    pause
    exit /b 1
)

REM 检查核心依赖是否存在，不存在则自动安装
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [WARN] 未检测到 Flask 库，正在自动安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] 依赖安装失败！请检查网络或手动运行 pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [INFO] 依赖安装成功！
)

echo [INFO] 正在启动服务器...
echo [INFO] 访问地址: http://localhost:5000
echo [INFO] 按 Ctrl+C 可停止服务

REM 5秒后自动打开浏览器
start "" cmd /c "timeout /t 5 >nul && start http://localhost:5000"

REM 启动 Flask 应用
python run.py

REM 如果 python run.py 意外退出，显示暂停
if errorlevel 1 (
    echo.
    echo [ERROR] 程序发生了异常退出。请查看上方的错误信息。
    pause
) else (
    echo [INFO] 程序已结束。
    pause
)
