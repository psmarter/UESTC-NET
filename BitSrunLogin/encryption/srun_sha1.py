#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Srun SHA1 加密实现
"""
import hashlib


def get_sha1(value: str) -> str:
    """
    SHA1 哈希
    """
    return hashlib.sha1(value.encode()).hexdigest()
