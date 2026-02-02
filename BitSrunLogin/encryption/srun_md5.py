#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Srun MD5 加密实现
"""
import hashlib


def get_md5(password: str, token: str) -> str:
    """
    使用 token 对密码进行 MD5 加密 (original)
    """
    return hashlib.md5((token + password).encode()).hexdigest()
