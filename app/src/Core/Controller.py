# 1. 核心控制模块（Core Controller）
# 职责：协调所有模块的交互，处理初始化流程和全局状态管理。
# 功能点：
# 启动时检查用户是否为首次使用（是否完成初始化）。
# 控制用户首次设置的流程（生成密钥、分片、存储配置）。
# 恢复时验证分片有效性并重组私钥。
# 管理用户会话（登录态、权限验证）。

import json
import os
import sys


# sys.path.append(os.path.abspath('../Gui'))


import Gui.HomeInterface
import Gui.SetupInterface


def hasInitialized():
    '''检查程序是否已初始化'''

    with open('./test/devConfig.json', 'r') as Config:
        data = json.load(Config)

    return data['General'][0]['IsInitialized']


# Core/Controller/WindowManager.py
from PySide6 import QtWidgets


class WindowManager:
    _app = None
    _current_window = None

    @classmethod
    def init_app(cls):
        if not cls._app:
            cls._app = QtWidgets.QApplication([])

    @classmethod
    def show_login(cls):
        cls._switch_window(Gui.HomeInterface.LoginWindow, 480, 360)

    @classmethod
    def show_setup(cls):
        cls._switch_window(Gui.SetupInterface.DatabaseSetupWindow, 800, 600)

    @classmethod
    def show_register(cls):
        cls._switch_window(Gui.HomeInterface.RegistrationWindow, 480, 360)

    @classmethod
    def _switch_window(cls, window_class, width, height):
        if cls._current_window:
            cls._current_window.close()
            cls._current_window.deleteLater()

        cls.init_app()
        cls._current_window = window_class()
        cls._current_window.resize(width, height)
        cls._current_window.show()
