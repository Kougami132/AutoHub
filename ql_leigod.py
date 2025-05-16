#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
name: 雷神自动暂停
cron: 0 6 * * *
"""

import requests
import hashlib
import time
from utils import get_config

def hash_password(password):
    md5_hash = hashlib.md5()
    password_bytes = password.encode("utf-8")
    md5_hash.update(password_bytes)
    hashed_password = md5_hash.hexdigest()
    return hashed_password


def generate_sign(params, key):
    def map_to_string(param):
        ks = sorted(param.keys())
        return "&".join([f"{k}={param[k]}" for k in ks])

    query_string = map_to_string(params)
    query_string += f"&key={key}"

    return hashlib.md5(query_string.encode()).hexdigest()


def create_session():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.leigod.com/",
            "Content-Type": "application/json",
        }
    )
    return session
    try:
        # 网页端接口
        url = base_url + "/api/auth/login/v1"
        req = session.post(url, json=data, timeout=20)
        if req.status_code == 200:
            print(req.json()['data'])
            account_token = req.json()["data"]["login_info"]["account_token"]
            token_data["account_token"] = account_token
            return True
            
        # 移动端接口
        url = base_url + "/wap/login/bind/v1"
        req = session.post(url, json=data, timeout=20)
        if req.status_code == 200:
            print(req.json()['data'])
            account_token = req.json()["data"]["login_info"]["account_token"]
            token_data["account_token"] = account_token
            return True
        elif req.status_code == 418:
            print("Request blocked by server (418).")
            return False
        else:
            print(req.text)
            return False
    except Exception as e:
        print("An error occurred: {}".format(e))
        return False

def check(session, data):
    try:
        url = base_url + "/api/user/info"
        req = session.post(url, json=data, timeout=20)
        if req.status_code == 200:
            print(req.json()['data'])
            return req.json()['data'].get('pause_status_id', 0) == 0, req.json()['data'].get('expiry_time', '')
        elif req.status_code == 418:
            print("Request blocked by server (418).")
            return False, ''
        else:
            print(req.text)
            return False, ''
    except Exception as e:
        print("An error occurred: {}".format(e))
        return False, ''

def pause(session, data):
    try:
        url = base_url + "/api/user/pause"
        req = session.post(url, json=data, timeout=20)
        if req.status_code == 200:
            print(req.json()['data'])
            return True
        elif req.status_code == 418:
            print("Request blocked by server (418).")
            return False
        else:
            print(req.text)
            return False
    except Exception as e:
        print("An error occurred: {}".format(e))
        return False

# 获取 account_token
account_token = get_config("leigod.account_token")
if not account_token:
    print("请在config.ini中配置 leigod.account_token")
    exit(1)

base_url = "https://webapi.leigod.com"

token_data = {
    "account_token": account_token,
    "lang": "zh_CN",
    "os_type": 4, # os_type 保持，与原 token_data 一致
}

session = create_session()

# 直接执行检查和暂停逻辑
enable_to_pause, expiry_time = check(session, token_data) # 'enable_to_pause' is True if pause_status_id == 0

if enable_to_pause:
    print("加速器当前为活动状态，尝试暂停...")
    if pause(session, token_data):
        # 尝试导入 modifyNotify，如果用户环境中有这个模块
        try:
            from modifyNotify import send
            send("雷神自动暂停", "已成功暂停雷神加速器。\n到期时间: {}".format(expiry_time))
        except ImportError:
            print("modifyNotify 模块未找到，跳过通知。")
        print("已成功暂停雷神加速器。到期时间: {}".format(expiry_time))
    else:
        print("暂停操作失败。")
elif expiry_time: # check 成功，但不是可暂停状态 (e.g., 已暂停 or other non-active status)
    # 检查 expiry_time 是否为空字符串，因为 check 在失败时可能返回 ('', False)
    if expiry_time: # 确保 expiry_time 有效才打印
        print("加速器当前非活动状态 (可能已暂停或过期)。无需操作。\n到期时间: {}".format(expiry_time))
    else: # API 请求可能失败，但 expiry_time 是空字符串，说明 check 返回了 (False, '')
        print("检查加速器状态成功，但当前非活动状态 (可能已暂停或过期)，且未获取到具体到期时间。无需操作。")
else: # check 返回 (False, '') 或 check 本身抛出异常后被捕获返回 (False, '')
    print("检查加速器状态失败，无法执行后续操作。")
