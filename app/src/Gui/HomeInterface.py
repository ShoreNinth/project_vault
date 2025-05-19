from PySide6 import QtCore, QtWidgets, QtGui, QtDBus
import sys
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QFormLayout, QVBoxLayout, QMessageBox
)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression


import Core.Controller
import Database.Courier


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("Hello", alignment=QtCore.Qt.AlignCenter)

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

        self.button_register = QtWidgets.QPushButton("Register")
        self.button_register.clicked.connect(self.register)

        self.recovery_label = QtWidgets.QLabel("Recovery Mode")
        self.recovery_button = QtWidgets.QPushButton("Recover")
        self.recovery_button.clicked.connect(self.recover)


        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.text, 0, 0, 1, 3)
        self.layout.addWidget(self.username, 2, 1, 1 ,2)
        self.layout.addWidget(self.username_label, 2, 0)
        self.layout.addWidget(self.password, 3, 1, 1, 2)
        self.layout.addWidget(self.password_label, 3, 0)
        self.layout.addWidget(self.button_login, 4, 1)
        self.layout.addWidget(self.button_register, 4, 2)
        self.layout.addWidget(self.recovery_label, 5, 0)
        self.layout.addWidget(self.recovery_button, 5, 2)

        # 设置组件的拉伸因子，用于放缩窗口时，组件等比例放大或者缩小
        # setRowStretch设置行的拉伸因子
        self.layout.setRowStretch(0, 1)
        # setColumnStretch设置行的拉伸因子
        self.layout.setColumnStretch(1, 1)


    @QtCore.Slot()
    def login_attempt(self):
        self.button_login.setText("Please wait")
        self.button_login.setEnabled(False)

    @QtCore.Slot()
    def recover(self):
        pass

    @QtCore.Slot()
    def register(self):
        self.close()
        Core.Controller.WindowManager.show_register()


def is_ascii(s):
    return all(ord(c) < 128 for c in s)

class RegistrationWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("用户注册")
        self.setup_ui()
        self.setMinimumSize(400, 250)

    def setup_ui(self):
        # 创建输入控件
        self.username_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.repeat_password_edit = QLineEdit()
        self.repeat_password_edit.setEchoMode(QLineEdit.Password)

        # 设置邮箱格式验证
        email_regex = QRegularExpression(r'^[\w\.-]+@[\w-]+\.[\w\.-]+$')
        email_validator = QRegularExpressionValidator(email_regex)
        self.email_edit.setValidator(email_validator)

        # 创建注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.validate_registration)

        # 设置布局
        form_layout = QFormLayout()
        form_layout.addRow("用户名:", self.username_edit)
        form_layout.addRow("邮箱:", self.email_edit)
        form_layout.addRow("密码:", self.password_edit)
        form_layout.addRow("重复密码:", self.repeat_password_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.register_btn)

        self.setLayout(main_layout)

    def validate_registration(self):
        # 获取输入值
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        repeat_password = self.repeat_password_edit.text()

        errors = []

        # 检查非空
        if not username:
            errors.append("用户名不能为空")
        if not email:
            errors.append("邮箱不能为空")
        if not password:
            errors.append("密码不能为空")
        if not repeat_password:
            errors.append("重复密码不能为空")

        # 检查ASCII字符
        if username and not is_ascii(username):
            errors.append("用户名必须为ASCII字符")
        if email and not is_ascii(email):
            errors.append("邮箱必须为ASCII字符")
        if password and not is_ascii(password):
            errors.append("密码必须为ASCII字符")

        # 验证邮箱格式
        if email and not re.match(r'^[\w\.-]+@[\w-]+\.[\w\.-]+$', email):
            errors.append("邮箱格式不正确")

        # 验证密码一致性
        if password and repeat_password and password != repeat_password:
            errors.append("两次输入的密码不一致")

        # 显示结果
        if errors:
            QMessageBox.critical(self, "输入错误", "\n".join(errors))
        else:
            QMessageBox.information(self, "注册成功", "用户注册成功！")
            # 这里可以添加实际注册逻辑
            print("Username: ", username)
            print("Email: ", email)
            print("Password: ", password)
            print("RepeatPassword: ", repeat_password)



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


