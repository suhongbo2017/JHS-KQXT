@echo off
rem -------------------------------------------------
rem  attendance_service Windows Service 控制脚本
rem  用法:
rem      service_control.bat install   # 注册服务并设为自动启动
rem      service_control.bat start     # 启动服务
rem      service_control.bat stop      # 停止服务
rem      service_control.bat remove    # 删除服务（先 stop）
rem -------------------------------------------------

set SERVICE_SCRIPT=attendance_service.py
set SERVICE_NAME=AttendanceService

if "%1"=="" (
    echo 用法: %0 [install^|start^|stop^|remove]
    exit /b 1
)

rem 必须以管理员身份运行
whoami /groups | find "S-1-5-32-544" >nul
if errorlevel 1 (
    echo 请右键 "cmd.exe" 选择 "以管理员身份运行"。
    exit /b 1
)

if /I "%1"=="install" (
    python %SERVICE_SCRIPT% install
    python %SERVICE_SCRIPT% setstarttype auto
    echo 已注册 %SERVICE_NAME% 为自动启动服务
) else if /I "%1"=="start" (
    python %SERVICE_SCRIPT% start
    echo 已启动 %SERVICE_NAME%
) else if /I "%1"=="stop" (
    python %SERVICE_SCRIPT% stop
    echo 已停止 %SERVICE_NAME%
) else if /I "%1"=="remove" (
    python %SERVICE_SCRIPT% remove
    echo 已删除 %SERVICE_NAME%
) else (
    echo 不支持的参数: %1
    exit /b 1
)
