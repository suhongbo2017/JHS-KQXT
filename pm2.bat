@echo off
setlocal enabledelayedexpansion

rem =============================
rem  PM2 管理脚本 (交互式)
rem  支持：Start, Stop, Restart, Status, Logs, Delete, Save, Exit
rem =============================

rem 项目根目录（请根据实际路径修改）
set "PROJECT_DIR=%~dp0"

:menu
cls
echo.
echo ==============================
echo   金恒晟系统 - PM2 管理工具
echo ==============================
echo 1. 启动服务 (Start)
echo 2. 停止服务 (Stop)
echo 3. 重启服务 (Restart)
echo 4. 查看状态 (Status)
echo 5. 查看实时日志 (Logs)
echo 6. 删除/关闭任务 (Delete)
echo 7. 保存开机自启 (Save)
echo 8. 退出 (Exit)
echo ==============================
set /p "choice=请输入数字选择操作: "

rem 切换到项目根目录
pushd "%PROJECT_DIR%"

if "%choice%"=="1" (
    pm2 start ecosystem.config.js
) else if "%choice%"=="2" (
    pm2 stop jhs-attendance
) else if "%choice%"=="3" (
    pm2 restart jhs-attendance
) else if "%choice%"=="4" (
    pm2 status
    pause
) else if "%choice%"=="5" (
    pm2 logs jhs-attendance
) else if "%choice%"=="6" (
    pm2 delete jhs-attendance
) else if "%choice%"=="7" (
    pm2 save
) else if "%choice%"=="8" (
    echo 退出脚本... && popd && exit /b 0
) else (
    echo 选项无效，请重新输入。
    pause
)

popd
goto menu
