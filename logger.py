#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
日志模块
"""
import logging
import os
from datetime import datetime

# 创建日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 创建日志文件名（按日期）
log_filename = os.path.join(LOG_DIR, f"uestc_net_{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('UESTC-NET')
