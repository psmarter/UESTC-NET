#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
持续在线监控脚本
定时检测网络连接，断网时自动重连并发送通知
"""
import os
import time
import platform
import ctypes
import requests
import sys

from logger import logger
from notifier import Notifier
from BitSrunLogin.LoginManager import LoginManager
from config import login_options, notify_options


# 连接性检测常量
PORTAL_KEYWORDS = (
    "srun_portal",
    "SRun",
    "login",
    "认证",
    "wlanacip",
    "wlanacname",
)
DEFAULT_TEST_URLS = (
    "http://connect.rom.miui.com/generate_204",
    "https://www.gstatic.com/generate_204",
    "http://www.baidu.com",
)

# 获取计算机名
HOSTNAME = platform.node()

# Windows 下禁用快速编辑模式（防止暂停）
try:
    if platform.system().lower() == 'windows':
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
except:
    pass

# Windows 控制台改为 UTF-8，避免表情/中文输出报错
if platform.system().lower() == 'windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def _build_session() -> requests.Session:
    """创建一个绕过系统代理的 Session。"""
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    return session


def _http_connected(session: requests.Session, urls) -> bool:
    """使用多个 HTTP 目标检测连通性，避免被 Portal 重定向误判。"""
    for url in urls:
        try:
            resp = session.get(url, timeout=4, allow_redirects=True)
            # 204 或空响应直接判定为在线
            if resp.status_code == 204 or (resp.status_code == 200 and not resp.text.strip()):
                return True

            if resp.encoding in (None, "ISO-8859-1"):
                resp.encoding = resp.apparent_encoding or "utf-8"
            text = resp.text

            # Portal 特征页面直接视为未联网
            if any(k.lower() in text.lower() for k in PORTAL_KEYWORDS) or any(k in (resp.url or "") for k in PORTAL_KEYWORDS):
                continue

            # 常见外网主页判断
            if "baidu" in (resp.url or "").lower() or "百度" in text:
                return True

            # 其他 2xx 但非 Portal 内容，也视为在线
            if 200 <= resp.status_code < 300:
                return True
        except requests.RequestException:
            continue
    return False


def is_connected(test_ip: str, test_urls=None) -> bool:
    """
    检查网络连接状态
    1) 优先使用 ping（无黑框）
    2) 失败时使用多目标 HTTP 检测并规避 Portal 重定向
    """
    import subprocess
    if test_ip:
        cmd = ["ping", "-n", "1", "-w", "2000", test_ip] if platform.system().lower() == 'windows' else ["ping", "-c", "1", "-W", "1", test_ip]

        # 使用 subprocess 替代 os.system 以避免黑框弹窗
        startupinfo = None
        creationflags = 0
        if platform.system().lower() == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    # 如果 ping 失败，尝试 HTTP 请求 (强制绕过代理)
    session = _build_session()
    urls = list(DEFAULT_TEST_URLS)
    if test_urls:
        # 用户自定义地址放在前面，默认地址兜底
        urls = list(dict.fromkeys(list(test_urls) + urls))
    return _http_connected(session, urls)


def do_login(notifier: Notifier) -> bool:
    """
    执行登录
    
    Returns:
        是否登录成功
    """
    user = login_options['user']
    
    try:
        manager = LoginManager(**login_options)
        result = manager.login(
            username=user.user_id,
            password=user.passwd
        )
        
        if result == "ok":
            logger.info(f"[{HOSTNAME}] 登录成功")
            notifier.notify_reconnect_success(HOSTNAME)
            return True
        else:
            logger.warning(f"[{HOSTNAME}] 登录失败: {result}")
            notifier.notify_reconnect_failure(HOSTNAME, result)
            return False
            
    except Exception as e:
        logger.error(f"[{HOSTNAME}] 登录异常: {e}")
        notifier.notify_reconnect_failure(HOSTNAME, str(e))
        return False


def monitor_loop():
    """主监控循环"""
    test_ip = login_options.get('test_ip', '223.5.5.5')
    test_urls = login_options.get('test_urls')
    delay = login_options.get('delay', 30)
    max_failed = login_options.get('max_failed', 3)
    
    # 初始化通知器
    notifier = Notifier(**notify_options)
    
    # 发送启动通知
    notifier.notify_startup(HOSTNAME)
    logger.info(f"[{HOSTNAME}] 网络监控服务已启动")
    logger.info(f"  检测间隔: {delay}s, 断网阈值: {max_failed}次")
    
    failed_count = 0
    was_offline = False
    current_delay = delay
    
    while True:
        try:
            if is_connected(test_ip, test_urls):
                # 网络正常
                if was_offline:
                    logger.info(f"[{HOSTNAME}] 网络已恢复")
                    was_offline = False
                failed_count = 0
                current_delay = delay
            else:
                # 网络异常
                failed_count += 1
                current_delay = max(5, current_delay // 2)  # 加快检测频率
                
                if failed_count >= max_failed:
                    if not was_offline:
                        logger.warning(f"[{HOSTNAME}] 检测到断网，尝试重连...")
                        notifier.notify_disconnect(HOSTNAME)
                        was_offline = True
                    
                    # 尝试重连
                    if do_login(notifier):
                        failed_count = 0
                        current_delay = delay
                    else:
                        # 重连失败,等待后重试
                        time.sleep(10)
            
            time.sleep(current_delay)
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在退出...")
            break
        except Exception as e:
            logger.error(f"监控循环异常: {e}")
            time.sleep(15)


def main():
    """主函数"""
    print("=" * 50)
    print("UESTC 校园网持续在线监控")
    print("=" * 50)
    print(f"主机名: {HOSTNAME}")
    print(f"按 Ctrl+C 停止监控")
    print("=" * 50)
    
    while True:
        try:
            monitor_loop()
            break
        except Exception as e:
            logger.error(f"程序异常，将在15秒后重启: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(15)


if __name__ == "__main__":
    main()
