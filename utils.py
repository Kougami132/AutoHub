#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import configparser
from typing import Any

def get_config(config_key: str, fallback: Any = None) -> Any:
    """
    获取配置项的值
    :param config_key: 配置项的键,格式为 'section.key'
    :param fallback: 默认返回值
    :return: 配置项的值
    
    示例:
    >>> get_config('leigod.username')  # 获取leigod区块下的username值
    >>> get_config('push.gobot_url')   # 获取push区块下的gobot_url值
    """
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        section, key = config_key.split('.')
        return config.get(section, key, fallback=fallback)
    except:
        return fallback


