@echo off
chcp 65001 >nul
echo ==========================================
echo UESTC 校园网自动登录 - 开机自启配置
echo ==========================================
echo.

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%always_online.py"

:: 检查 Python 环境 (优先使用 py 启动器)
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [Check] 发现 py 启动器，正在解析 pythonw 绝对路径...
    for /f "delims=" %%i in ('py -c "import sys; import os; print(os.path.join(os.path.dirname(sys.executable), 'pythonw.exe'))"') do set "PYTHON_CMD=%%i"
    goto :create_task
)

:: 备选：检查 pythonw
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=pythonw"
    echo [Check] 发现 pythonw，将使用 pythonw 运行脚本
    goto :create_task
)

echo [错误] 未找到 py 或 pythonw，请安装 Python！
echo 推荐访问 python.org 下载安装。
pause
exit /b 1

:create_task
echo 脚本路径: %SCRIPT_PATH%
echo.

:: 创建 VBS 启动脚本（静默运行） - 提前创建以供后续使用
echo 正在准备启动脚本...
set "VBS_PATH=%SCRIPT_DIR%start_silent.vbs"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%SCRIPT_DIR%"
echo WshShell.Run "%PYTHON_CMD% ""%SCRIPT_PATH%""", 0, False
) > "%VBS_PATH%"


:: 创建任务计划
echo [1/2] 正在创建开机自启动任务...
schtasks /delete /tn "UESTC-NET" /f >nul 2>&1
schtasks /create /tn "UESTC-NET" /tr "\"%PYTHON_CMD%\" \"%SCRIPT_PATH%\"" /sc onlogon /rl highest /f

if %errorlevel% equ 0 (
    echo [成功] 开机自启动任务已创建！
) else (
    echo [失败] 任务创建失败，可能需要管理员权限。
    echo 尝试使用启动文件夹方式...
    goto :startup_folder
)



echo.
echo ==========================================
echo 配置完成！
echo ==========================================
echo.
echo 下次开机登录后，脚本将自动运行。
echo.
echo 测试方法：
echo   1. 手动运行: py always_online.py
echo   2. 或双击: start_silent.vbs
echo.
pause
exit /b 0

:startup_folder
:: 备选方案：复制到启动文件夹
echo 正在使用启动文件夹方式...
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy "%VBS_PATH%" "%STARTUP%\UESTC-NET.vbs" >nul
if %errorlevel% equ 0 (
    echo [成功] 已添加到启动文件夹！
) else (
    echo [失败] 请手动将 start_silent.vbs 复制到启动文件夹
)
pause
exit /b 0
