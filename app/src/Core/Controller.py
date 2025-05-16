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


class WindowManager:
    # 使用类变量保存 app 实例
    app = None

    @classmethod
    def Login(cls):
        if not cls.app:
            cls.app = Gui.HomeInterface.QtWidgets.QApplication([])

        widget = Gui.HomeInterface.LoginWindow()
        widget.resize(480, 360)
        widget.show()
        cls.app.exec()

    @classmethod
    def Main(cls):
        if not cls.app:
            cls.app = Gui.HomeInterface.QtWidgets.QApplication([])

        widget = Gui.HomeInterface.MainWindow()
        widget.resize(800, 600)
        widget.show()
        cls.app.exec()

    @classmethod
    def Setup(cls):
        if not cls.app:
            cls.app = Gui.SetupInterface.QApplication([])

        widget = Gui.SetupInterface.DatabaseSetupWindow()
        widget.resize(800, 600)
        widget.show()
        cls.app.exec()
