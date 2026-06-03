@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
rem =============================
rem  PM2 管理脚本 (交互式)
rem  支持：Start, Stop, Restart, Status, Logs, Delete, Save, Exit, Install Startup
rem =============================

rem 项目根目录（请根据实际路径修改）
set "PROJECT_DIR=%~dp0"
rem 激活 uv 创建的虚拟环境
if exist "%PROJECT_DIR%.venv\Scripts\activate.bat" (
    call "%PROJECT_DIR%.venv\Scripts\activate.bat"
) else (
    echo 未检测到 .venv 虚拟环境，请运行 "uv venv .venv" 并重新运行此脚本。
    pause
    exit /b 1
)
if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"

rem 若通过参数传入选择，则直接使用；否则进入交互式菜单
if not "%~1"=="" (
    set "choice=%~1"
    goto process_choice
)

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
echo 9. 安装开机自启 (Install Startup)
echo ==============================
set /p "choice=请输入数字选择操作: "

:process_choice
rem 切换到项目根目录
pushd "%PROJECT_DIR%"

if "%choice%"=="1" (
    where pm2 >nul 2>&1
    if errorlevel 1 (
        echo 未检测到 pm2，请先使用 npm install -g pm2 安装。 && pause && popd && exit /b 1
    ) else (
        echo 正在启动考勤服务...
        pm2 start ecosystem.config.js --log "%PROJECT_DIR%logs\\jhs-attendance.log" --output "%PROJECT_DIR%logs\\out.log" --error "%PROJECT_DIR%logs\\err.log"
        if errorlevel 1 (
            echo 启动失败，请检查 pm2 配置。
        ) else (
            echo 服务已启动。
        )
        pm2 save
        set "choice="
        goto menu
    )
    goto menu
) else if "%choice%"=="2" (
    pm2 stop jhs-attendance
    goto menu
) else if "%choice%"=="3" (
    pm2 restart jhs-attendance
    goto menu
) else if "%choice%"=="4" (
    pm2 status
    pause
    goto menu
) else if "%choice%"=="5" (
    pm2 logs jhs-attendance
    goto menu
) else if "%choice%"=="6" (
    pm2 delete jhs-attendance
    goto menu
) else if "%choice%"=="7" (
    pm2 save
    goto menu
) else if "%choice%"=="9" (
    pm2 startup windows -u %USERNAME%
    pm2 install pm2-logrotate
    pm2 set pm2-logrotate:max_size 5M
    pm2 set pm2-logrotate:retain 5
    pm2 set pm2-logrotate:compress true
    pm2 save
    goto menu
) else if "%choice%"=="8" (
    echo 退出脚本... && popd && exit /b 0
) else (
    echo 选项无效，请重新输入。
    pause
    popd
    goto menu
)

popd
exit /b 0
