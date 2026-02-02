#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
一次性登录脚本
"""
import sys
import platform
from BitSrunLogin.LoginManager import LoginManager
from always_online import is_connected
from config import login_options

# Windows 控制台默认 GBK，UTF-8 表情会报编码错误；强制切换输出编码
if platform.system().lower() == 'windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def main():
    """执行一次性登录"""
    print("=" * 50)
    print("UESTC 校园网自动认证登录")
    print("=" * 50)
    
    # Check if already connected
    test_ip = login_options.get('test_ip', '223.5.5.5')
    test_urls = login_options.get('test_urls')
    if is_connected(test_ip, test_urls):
        print("\n✅ 检测到网络已连接，无需重复登录。")
        return

    user = login_options['user']
    
    try:
        manager = LoginManager(**login_options)
        result = manager.login(
            username=user.user_id,
            password=user.passwd
        )
        
        if result == "ok":
            print("\n✅ 登录成功！")
        else:
            print(f"\n❌ 登录失败: {result}")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
