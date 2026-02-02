#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
调试脚本 - 用于诊断登录脚本问题
"""
import sys
import os

print("=" * 50)
print("UESTC-NET 调试脚本")
print("=" * 50)

# 1. 检查 Python 版本
print(f"\n[1] Python 版本: {sys.version}")

# 2. 检查代理设置
print("\n[2] 代理环境变量:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
for var in proxy_vars:
    value = os.environ.get(var, '未设置')
    print(f"    {var}: {value}")

# 3. 检查 requests 库
print("\n[3] 检查依赖库:")
try:
    import requests
    print(f"    requests: OK (版本 {requests.__version__})")
except ImportError as e:
    print(f"    requests: 错误 - {e}")
    sys.exit(1)

# 4. 检查本地模块
print("\n[4] 检查本地模块:")
try:
    from BitSrunLogin.LoginManager import LoginManager
    print("    BitSrunLogin.LoginManager: OK")
except Exception as e:
    print(f"    BitSrunLogin.LoginManager: 错误 - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from config import login_options
    print(f"    config: OK")
    print(f"    认证地址: {login_options.get('url')}")
    print(f"    用户: {login_options.get('user').user_id if login_options.get('user') else 'N/A'}")
except Exception as e:
    print(f"    config: 错误 - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试网络连接（绕过代理）
print("\n[5] 测试网络连接 (绕过代理):")
auth_url = login_options.get('url', 'http://10.253.0.237')

# 禁用代理
session = requests.Session()
session.trust_env = False  # 忽略环境变量中的代理设置
session.proxies = {'http': None, 'https': None}

try:
    response = session.get(auth_url, timeout=10)
    print(f"    认证服务器 {auth_url}: 可达 (状态码 {response.status_code})")
    if 'user_ip' in response.text:
        import re
        match = re.search(r'id="user_ip"\s*value="(.*?)"', response.text)
        if match:
            print(f"    检测到本机 IP: {match.group(1)}")
except Exception as e:
    print(f"    认证服务器: 连接失败 - {e}")

# 6. 测试外网连接
print("\n[6] 测试外网连接:")
try:
    response = session.get("http://www.baidu.com", timeout=5)
    if response.status_code == 200:
        print("    外网: 已连通 (您已完成认证)")
    else:
        print(f"    外网: 状态码 {response.status_code}")
except Exception as e:
    print(f"    外网: 未连通 - {e}")
    print("    (这说明您可能需要先认证)")

print("\n" + "=" * 50)
print("调试完成！")
print("=" * 50)
