@echo off
chcp 65001 >nul
echo ==========================================
echo UESTC 校园网自动登录 - 停止与卸载
echo ==========================================
echo.

echo [1/3] 正在停止后台进程...
taskkill /F /IM pyw.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
echo √ 进程已终止

echo [2/3] 正在删除开机自启任务...
schtasks /delete /tn "UESTC-NET" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo √ 任务已删除
) else (
    echo ! 任务删除失败（可能已删除或无权限）
)

echo [3/3] 清理启动文件夹...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\UESTC-NET.vbs" >nul 2>&1
echo √ 清理完成

echo.
echo ==========================================
echo 服务已彻底停止，且不会再开机自启。
echo ==========================================
echo.
pause
