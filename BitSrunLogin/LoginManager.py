#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
深澜 (Srun) Portal 登录管理器
"""
import re
import requests

from ._decorators import (
    infomanage, checkvars, checkip, checktoken, checkinfo, checkmd5,
    checkencryptedinfo, checkencryptedmd5, checkchkstr, checkencryptedchkstr
)
from .encryption.srun_md5 import get_md5
from .encryption.srun_sha1 import get_sha1
from .encryption.srun_base64 import get_base64
from .encryption.srun_xencode import get_xencode


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def create_session():
    """创建一个绕过系统代理的 Session"""
    session = requests.Session()
    # 禁用环境变量中的代理设置（解决 Clash/V2Ray 等代理软件干扰）
    session.trust_env = False
    session.proxies = {'http': None, 'https': None}
    return session


class LoginManager:
    """深澜认证登录管理器"""
    
    def __init__(self, **kwargs):
        # 默认配置
        self.args = {
            'url': 'http://10.253.0.237',
            'url_login_page': "/",
            'url_get_challenge_api': "/cgi-bin/get_challenge",
            'url_login_api': "/cgi-bin/srun_portal",
            'n': "200",
            'vtype': "1",
            'ac_id': "1",
            'enc': "srun_bx1",
            'domain': "@dx-uestc",
        }
        
        # 更新用户配置
        self.args.update(kwargs)
        
        # 构建完整 URL
        self.args['url_login_page'] = self.args['url'] + self.args['url_login_page']
        self.args['url_get_challenge_api'] = self.args['url'] + self.args['url_get_challenge_api']
        self.args['url_login_api'] = self.args['url'] + self.args['url_login_api']
        
        # 初始化 HTTP Session（绕过代理）
        self.session = create_session()
        
        # 初始化状态变量
        self.username = None
        self.password = None
        self.ip = "0.0.0.0"  # 默认 IP，后续从 challenge 响应中更新
        self.token = None
        self.info = None
        self.md5 = None
        self.encrypted_info = None
        self.encrypted_md5 = None
        self.chkstr = None
        self.encrypted_chkstr = None
        self._login_result = None

    def login(self, username: str, password: str) -> str:
        """
        执行登录流程
        
        Args:
            username: 学号
            password: 密码
            
        Returns:
            登录结果字符串
        """
        base_username = str(username)
        domain = self.args.get('domain', "")
        # 防止用户已填写后缀时重复附加
        if domain and not base_username.endswith(domain):
            self.username = base_username + domain
        else:
            self.username = base_username
        self.password = str(password)
        
        self.get_ip()
        self.get_token()
        self.get_login_response()
        
        return self._login_result

    def get_ip(self):
        """Step 1: 获取本机 IP"""
        print("Step1: 获取服务器返回的本机 IP")
        self._get_login_page()
        self._resolve_ip_from_login_page()
        print("-" * 40)

    def get_token(self):
        """Step 2: 获取认证 Token"""
        print("Step2: 获取认证 Token")
        self._get_challenge()
        self._resolve_token_from_challenge_response()
        print("-" * 40)

    def get_login_response(self):
        """Step 3: 发送登录请求并获取结果"""
        print("Step3: 发送登录请求")
        self._generate_encrypted_login_info()
        self._send_login_info()
        self._resolve_login_response()
        print(f"登录结果: {self._login_result}")
        print("-" * 40)

    @infomanage(
        callinfo="正在获取登录页面",
        successinfo="成功获取登录页面",
        errorinfo="获取登录页面失败"
    )
    def _get_login_page(self):
        self._page_response = self.session.get(
            self.args['url_login_page'], 
            headers=HEADER,
            timeout=10
        )

    @checkvars(
        varlist="_page_response",
        errorinfo="缺少登录页面响应"
    )
    @infomanage(
        callinfo="正在解析 IP 地址",
        successinfo="成功获取 IP",
        errorinfo="解析 IP 失败"
    )
    def _resolve_ip_from_login_page(self):
        match = re.search(r'id="user_ip"\s*value="(.*?)"', self._page_response.text)
        if match:
            self.ip = match.group(1)
            print(f"    IP: {self.ip}")
        else:
            # 解析失败不报错，改用 API获取
            print("    注意: 无法从页面解析 IP，将尝试通过 API 获取")

    @checkip
    @infomanage(
        callinfo="正在获取 Challenge",
        successinfo="成功获取 Challenge",
        errorinfo="获取 Challenge 失败"
    )
    def _get_challenge(self):
        params = {
            "callback": "jsonp_callback",
            "username": self.username,
            "ip": self.ip
        }
        self._challenge_response = self.session.get(
            self.args['url_get_challenge_api'],
            params=params,
            headers=HEADER,
            timeout=10
        )

    @checkvars(
        varlist="_challenge_response",
        errorinfo="缺少 Challenge 响应"
    )
    @infomanage(
        callinfo="正在解析 Token",
        successinfo="成功获取 Token",
        errorinfo="解析 Token 失败"
    )
    def _resolve_token_from_challenge_response(self):
        # 解析 Token
        match = re.search(r'"challenge":"(.*?)"', self._challenge_response.text)
        if match:
            self.token = match.group(1)
            print(f"    Token: {self.token}")
        else:
            raise ValueError("无法从 Challenge 响应解析 Token")
            
        # 解析并更新 Client IP
        ip_match = re.search(r'"client_ip":"(.*?)"', self._challenge_response.text)
        if ip_match:
            self.ip = ip_match.group(1)
            print(f"    获取到真实 IP: {self.ip}")

    @checkip
    def _generate_info(self):
        """生成 info 字段"""
        import json
        info_params = {
            "username": self.username,
            "password": self.password,
            "ip": self.ip,
            "acid": str(self.args['ac_id']),
            "enc_ver": self.args['enc']
        }
        # 使用 standard JSON dump, 去除空格
        self.info = json.dumps(info_params, separators=(',', ':'))

    @checkinfo
    @checktoken
    def _encrypt_info(self):
        """加密 info 字段"""
        self.encrypted_info = "{SRBX1}" + get_base64(get_xencode(self.info, self.token))

    @checktoken
    def _generate_md5(self):
        """生成 MD5"""
        self.md5 = get_md5(self.password, self.token)

    @checkmd5
    def _encrypt_md5(self):
        """加密 MD5"""
        self.encrypted_md5 = "{MD5}" + self.md5

    @checktoken
    @checkip
    @checkencryptedinfo
    def _generate_chksum(self):
        """生成校验字符串"""
        self.chkstr = self.token + self.username
        self.chkstr += self.token + self.md5
        self.chkstr += self.token + self.args['ac_id']
        self.chkstr += self.token + self.ip
        self.chkstr += self.token + self.args['n']
        self.chkstr += self.token + self.args['vtype']
        self.chkstr += self.token + self.encrypted_info

    @checkchkstr
    def _encrypt_chksum(self):
        """加密校验字符串"""
        self.encrypted_chkstr = get_sha1(self.chkstr)

    def _generate_encrypted_login_info(self):
        """生成所有加密登录信息"""
        self._generate_info()
        self._encrypt_info()
        self._generate_md5()
        self._encrypt_md5()
        self._generate_chksum()
        self._encrypt_chksum()

    @checkip
    @checkencryptedmd5
    @checkencryptedinfo
    @checkencryptedchkstr
    @infomanage(
        callinfo="正在发送登录信息",
        successinfo="登录信息发送成功",
        errorinfo="发送登录信息失败"
    )
    def _send_login_info(self):
        """发送登录请求"""
        params = {
            'callback': 'jsonp_callback',
            'action': 'login',
            'username': self.username,
            'password': self.encrypted_md5,
            'ac_id': self.args['ac_id'],
            'ip': self.ip,
            'chksum': self.encrypted_chkstr,
            'info': self.encrypted_info,
            'n': self.args['n'],
            'type': self.args['vtype'],
            'os': 'Windows 10',
            'name': 'Windows',
            'double_stack': 0
        }
        self._login_response = self.session.get(
            self.args['url_login_api'],
            params=params,
            headers=HEADER,
            timeout=10
        )

    @checkvars(
        varlist="_login_response",
        errorinfo="缺少登录响应"
    )
    @infomanage(
        callinfo="正在解析登录结果",
        successinfo="登录结果解析成功",
        errorinfo="解析登录结果失败"
    )
    def _resolve_login_response(self):
        """解析登录响应"""
        match = re.search(r'"error":"(.*?)"', self._login_response.text)
        if match:
            self._login_result = match.group(1)
        else:
            self._login_result = "unknown"
        
        # 打印完整响应用于调试
        if self._login_result != "ok":
            print(f"    响应: {self._login_response.text[:200]}")
