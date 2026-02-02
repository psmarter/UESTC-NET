#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
UESTC 校园网自动认证 - 配置模板

使用说明：
1. 复制此文件为 config.py
2. 填入你的账号信息
3. config.py 已被 .gitignore 排除，不会被提交到 Git
"""
from collections import namedtuple

User = namedtuple('User', ['user_id', 'passwd'])

# ==================== 登录配置 ====================
login_options = {
    # 账号信息（填入你的学号和密码）
    'user': User('你的学号', '你的密码'),

    # 认证页面地址
    # 研究院/主楼通常使用: http://10.253.0.237 或 http://10.253.0.235
    'url': "http://10.253.0.237",

    # ac_id 参数（可能需要根据实际情况调整）
    # 主楼有线校园网: 1
    # 寝室公寓: 3
    'ac_id': '1',

    # 网络提供商类型
    # 校园网教育网: @dx-uestc
    # 电信: @dx
    # 移动: @cmcc
    'domain': '@dx-uestc',

    # ========== 以下参数一般不需要修改 ==========
    'test_ip': "223.5.5.5",         # 用于检测网络连通性的 IP（AliDNS，Ping 更稳定）
    'test_urls': [                  # HTTP 连通性检测地址（Ping 失败时兜底）
        "http://connect.rom.miui.com/generate_204",
        "https://www.gstatic.com/generate_204",
        "http://www.baidu.com"
    ],
    'delay': 30,                    # 检测间隔（秒）
    'max_failed': 3,                # 连续失败多少次视为断网
}

# ==================== 通知配置 ====================
notify_options = {
    'enabled': False,               # 默认关闭通知，如需开启改为 True
    
    # 企业微信机器人 Webhook URL
    # 获取方式：企业微信群 -> 添加机器人 -> 复制 Webhook 地址
    'wechat_webhook': '',  # 填入你的 Webhook URL
    
    # 通知场景
    'notify_on_disconnect': True,   # 断网时通知
    'notify_on_reconnect': True,    # 重连成功时通知
    'notify_on_failure': True,      # 重连失败时通知
}
