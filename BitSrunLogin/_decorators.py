#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
装饰器模块 - 用于检查变量和管理函数执行信息
"""
from functools import wraps


def infomanage(callinfo="", successinfo="", errorinfo=""):
    """管理函数调用信息的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if callinfo:
                print(f"  {callinfo}...")
            try:
                result = func(*args, **kwargs)
                if successinfo:
                    print(f"  √ {successinfo}")
                return result
            except Exception as e:
                if errorinfo:
                    print(f"  × {errorinfo}: {e}")
                raise
        return wrapper
    return decorator


def checkvars(varlist="", errorinfo=""):
    """检查对象属性是否已定义的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if isinstance(varlist, str):
                vars_to_check = [varlist]
            else:
                vars_to_check = varlist
            for var in vars_to_check:
                if not hasattr(self, var) or getattr(self, var) is None:
                    raise ValueError(f"{errorinfo}: {var} is not defined")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def checkip(func):
    """检查 IP 是否已获取"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'ip') or self.ip is None:
            raise ValueError("IP address is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checktoken(func):
    """检查 token 是否已获取"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'token') or self.token is None:
            raise ValueError("Token is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkinfo(func):
    """检查 info 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'info') or self.info is None:
            raise ValueError("Info is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkmd5(func):
    """检查 MD5 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'md5') or self.md5 is None:
            raise ValueError("MD5 is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkencryptedinfo(func):
    """检查加密 info 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'encrypted_info') or self.encrypted_info is None:
            raise ValueError("Encrypted info is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkencryptedmd5(func):
    """检查加密 MD5 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'encrypted_md5') or self.encrypted_md5 is None:
            raise ValueError("Encrypted MD5 is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkchkstr(func):
    """检查 chkstr 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'chkstr') or self.chkstr is None:
            raise ValueError("Checksum string is not defined")
        return func(self, *args, **kwargs)
    return wrapper


def checkencryptedchkstr(func):
    """检查加密 chkstr 是否已生成"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'encrypted_chkstr') or self.encrypted_chkstr is None:
            raise ValueError("Encrypted checksum string is not defined")
        return func(self, *args, **kwargs)
    return wrapper
