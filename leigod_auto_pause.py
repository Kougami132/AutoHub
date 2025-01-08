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
import json

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


def login(session, data):
    try:
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



username = get_config("leigod.username")
password = hash_password(get_config("leigod.password"))
if not username or not password:
    print("请在config.ini中配置账号信息")
    exit(1)
base_url = "https://webapi.leigod.com"
key = "5C5A639C20665313622F51E93E3F2783"  # 密钥

# 获取当前时间戳
ts = str(int(time.time()))

token_data = {
    "account_token": None,
    "lang": "zh_CN",
    "os_type": 4,
}

login_data = {
    "country_code": 86,
    "lang": "zh_CN",
    "password": "{}".format(password),
    "region_code": 1,
    "src_channel": "guanwang",
    "username": "{}".format(username),
    "ts": ts,
    "mobile_num": "{}".format(username),
    "os_type": 4,
}

# 生成 sign 值
sign = generate_sign(login_data, key)
login_data["sign"] = sign

session = create_session()

if login(session, login_data):
    enable, expiry_time = check(session, token_data)
    if enable and pause(session, token_data):
        from notify import send
        send("雷神自动暂停", "已暂停雷神加速器\n剩余时间: {}".format(expiry_time))