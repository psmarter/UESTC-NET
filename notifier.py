#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
通知模块 - 支持企业微信 Webhook 通知
"""
import json
import requests
from datetime import datetime


class Notifier:
    """通知管理器"""
    
    def __init__(self, **options):
        self.enabled = options.get('enabled', False)
        self.wechat_webhook = options.get('wechat_webhook', '')
        self.notify_on_disconnect = options.get('notify_on_disconnect', True)
        self.notify_on_reconnect = options.get('notify_on_reconnect', True)
        self.notify_on_failure = options.get('notify_on_failure', True)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def send_wechat(self, title: str, content: str) -> bool:
        """
        发送企业微信通知
        
        Args:
            title: 消息标题
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        if not self.wechat_webhook:
            return False
        
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"### {title}\n\n{content}\n\n> {self._get_timestamp()}"
                }
            }
            
            response = requests.post(
                self.wechat_webhook,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data),
                timeout=10
            )
            
            result = response.json()
            return result.get('errcode', -1) == 0
            
        except Exception as e:
            print(f"发送微信通知失败: {e}")
            return False
    
    def notify_disconnect(self, hostname: str):
        """通知断网"""
        if self.enabled and self.notify_on_disconnect:
            self.send_wechat(
                "⚠️ 校园网断开",
                f"**主机**: {hostname}\n\n检测到网络断开，正在尝试重新连接..."
            )
    
    def notify_reconnect_success(self, hostname: str):
        """通知重连成功"""
        if self.enabled and self.notify_on_reconnect:
            self.send_wechat(
                "✅ 校园网已恢复",
                f"**主机**: {hostname}\n\n网络已成功重新连接！"
            )
    
    def notify_reconnect_failure(self, hostname: str, error: str):
        """通知重连失败"""
        if self.enabled and self.notify_on_failure:
            self.send_wechat(
                "❌ 校园网重连失败",
                f"**主机**: {hostname}\n\n重连失败，需要手动处理。\n\n**错误**: {error}"
            )
    
    def notify_startup(self, hostname: str):
        """通知服务启动"""
        if self.enabled:
            self.send_wechat(
                "🚀 校园网监控已启动",
                f"**主机**: {hostname}\n\n自动登录服务已开始运行。"
            )
