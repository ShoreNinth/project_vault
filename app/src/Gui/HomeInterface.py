import os
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui, QtDBus




class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        # 用户名输入框
        self.username = QtWidgets.QLineEdit(self)
        self.username.setPlaceholderText("Username")
        self.username_label = QtWidgets.QLabel("username")

        # 密码输入框，允许一键清除、隐藏字符
        self.password = QtWidgets.QLineEdit(self)
        self.password.setClearButtonEnabled(True)
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Password")
        self.password_label = QtWidgets.QLabel("password")

        self.button_login = QtWidgets.QPushButton("Login")
        self.button_login.setShortcut("Enter")
        self.button_login.clicked.connect(self.login_attempt)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.text, 0, 0, 1, 2)
        self.layout.addWidget(self.username, 2, 1)
        self.layout.addWidget(self.username_label, 2, 0)
        self.layout.addWidget(self.password, 3, 1)
        self.layout.addWidget(self.password_label, 3, 0)
        self.layout.addWidget(self.button_login, 4, 1)

        # 设置组件的拉伸因子，用于放缩窗口时，组件等比例放大或者缩小
        # setRowStretch设置行的拉伸因子
        self.layout.setRowStretch(0, 1)
        # setColumnStretch设置行的拉伸因子
        self.layout.setColumnStretch(1, 1)


    @QtCore.Slot()
    def login_attempt(self):
        self.button_login.setText("Please wait")
        self.button_login.setEnabled(False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QGridLayout(central_widget)

        # 添加内容
        self.welcome_text = QtWidgets.QLabel("Welcome back!", alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.welcome_text, 0, 0, 1, 2)


        menubar = self.menuBar()

        self.openfile = QtGui.QAction('打开文件')
        self.openfile.triggered.connect(lambda: print('打开文件'))

        self.closefile = QtGui.QAction('关闭文件')
        self.closefile.triggered.connect(lambda: print('关闭文件'))

        # 创建并添加菜单
        fileMenu = menubar.addMenu('文件')
        fileMenu.addAction(self.openfile)
        fileMenu.addAction(self.closefile)

class AboutWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QGridLayout(central_widget)

        self.button_about_Qt= QtWidgets.QPushButton("About Qt")
        layout.addWidget(self.button_about_Qt, 0, 0)


