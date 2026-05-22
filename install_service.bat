# 安装 Windows 服务（使用 NSSM）
@echo off
setlocal

:: 请自行下载 NSSM 并解压到 C:\nssm\bin 目录（或自行修改路径）
set NSSM_PATH=C:\nssm\bin\nssm.exe

:: 项目根目录（请根据实际路径修改）
set PROJECT_DIR=d:\VSCODE\PYTHON3\考勤查询

:: Python 可执行文件路径（使用 uv 时，uv 会在环境中调用 python）
set PYTHON_EXE=python

:: 服务名称
set SERVICE_NAME=AttendanceService

:: 进入项目目录
cd /d "%PROJECT_DIR%"

:: 安装服务
"%NSSM_PATH%" install "%SERVICE_NAME%" "%PYTHON_EXE%" "app.py"

:: 设置服务的工作目录（确保能找到 app.py）
"%NSSM_PATH%" set "%SERVICE_NAME%" AppDirectory "%PROJECT_DIR%"

:: 设置服务启动方式为自动
"%NSSM_PATH%" set "%SERVICE_NAME%" Start "SERVICE_AUTO_START"

:: 启动服务
"%NSSM_PATH%" start "%SERVICE_NAME%"

echo Service "%SERVICE_NAME%" 已安装并启动。
endlocal
