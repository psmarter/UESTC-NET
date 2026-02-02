@echo off
REM UESTC 校园网自动登录 - 后台运行脚本

cd /d "%~dp0"
start /b pythonw always_online.py

echo 服务已在后台启动
echo 日志文件位于 logs 目录
pause
