#!/usr/bin/python3

import json
import os
import platform
import sys


class GetSystemLang:

    def linux_get_lang():
        """Linux/UNIX/MACOS"""
        user_locale = os.getenv('LANGUAGE')
        return user_locale

    def nt_get_lang():
        """Windows"""
        # TODO
        # Windows测试
        language = platform.win32_ver()[0]
        return language

    def get_lang():
        """判断操作系统类型"""
        if sys.platform == 'linux':
            return GetSystemLang.linux_get_lang()
        else:
            return GetSystemLang.nt_get_lang()

def load_locale(locale):
    """读取本地化"""

    match locale:
        case 'en_US':
            return "English"
        case 'zh_CN':
            return "简体中文"



    try:
        with open('./config/user_conf.json', 'r') as Config:
            data = json.load(Config)
    except FileNotFoundError:
        print('File_not_found')


    return data['General'][0]['IsInitialized']
