import hashlib
import re
import os

from PySide6 import QtCore, QtWidgets, QtGui, QtDBus
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QFormLayout, QVBoxLayout, QMessageBox, QFileDialog, QRadioButton, QCheckBox, QComboBox
)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit,
                               QStackedWidget, QFrame, QScrollArea)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette
from PySide6.QtCore import Qt, QSize, Signal, QTimer

import Core.Controller
import Core.FileDigester
import Database.Courier
import Database.Gatekeeper
import Log.LoginLogger


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text = QtWidgets.QLabel("欢迎回来！", alignment=QtCore.Qt.AlignCenter)

        self.server_domain_label=QtWidgets.QLabel("服务器地址")
        self.server_domain = QtWidgets.QLineEdit("localhost")
        self.server_port_label = QtWidgets.QLabel("服务器端口")
        self.server_port = QtWidgets.QLineEdit("3306")

        # 用户名输入框
        self.username = QtWidgets.QLineEdit(self)
        self.username.setPlaceholderText("用户名/邮箱")
        self.username_label = QtWidgets.QLabel("用户名/邮箱")

        # 密码输入框，允许一键清除、隐藏字符
        self.password = QtWidgets.QLineEdit(self)
        self.password.setClearButtonEnabled(True)
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("密码")
        self.password_label = QtWidgets.QLabel("密码")

        self.button_login = QtWidgets.QPushButton("登录")
        self.button_login.setShortcut("Enter")
        self.button_login.clicked.connect(self.login_attempt)

        self.button_register = QtWidgets.QPushButton("注册")
        self.button_register.clicked.connect(self.register)

        self.recovery_label = QtWidgets.QLabel("分片丢失？进入恢复模式")
        self.recovery_button = QtWidgets.QPushButton("恢复模式")
        self.recovery_button.clicked.connect(self.recover)


        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.text, 0, 0, 1, 3)
        self.layout.addWidget(self.server_domain, 2, 1, 1 ,2)
        self.layout.addWidget(self.server_domain_label, 2, 0)
        self.layout.addWidget(self.server_port, 3, 1, 1,2)
        self.layout.addWidget(self.server_port_label, 3, 0)
        self.layout.addWidget(self.username, 4, 1, 1 ,2)
        self.layout.addWidget(self.username_label, 4, 0)
        self.layout.addWidget(self.password, 5, 1, 1, 2)
        self.layout.addWidget(self.password_label, 5, 0)
        self.layout.addWidget(self.button_login, 6, 1)
        self.layout.addWidget(self.button_register, 6, 2)
        self.layout.addWidget(self.recovery_label, 7, 1)
        self.layout.addWidget(self.recovery_button, 7, 2)


        # 设置组件的拉伸因子，用于放缩窗口时，组件等比例放大或者缩小
        # setRowStretch设置行的拉伸因子
        self.layout.setRowStretch(0, 1)
        # setColumnStretch设置行的拉伸因子
        self.layout.setColumnStretch(1, 1)

    @QtCore.Slot()
    def login_attempt(self):
        """登录验证流程优化"""
        identifier = self.username.text().strip()
        password = self.password.text()

        # 输入验证
        if not identifier or not password:
            self.show_error("用户名/邮箱和密码不能为空")
            return

        # 显示加载状态
        self.button_login.setEnabled(False)

        # 使用线程防止界面冻结
        login_thread = LoginThread(identifier, password)
        login_thread.result_signal.connect(self.handle_login_result)
        login_thread.start()

    def handle_login_result(self, result):
        """处理登录结果"""
        self.button_login.setEnabled(True)
        self.button_login.setText("Login")

        if isinstance(result, Exception):
            self.show_error(f"登录失败: {str(result)}")
        elif result:
            Core.Controller.WindowManager.show_main()
            self.close()
        else:
            self.show_error("用户名/邮箱或密码错误")

        Core.Controller.WindowManager.show_main()


    def show_error(self, message):
        """显示错误提示"""
        Log.LoginLogger.login_error_log(message)


    @QtCore.Slot()
    def recover(self):
        Core.Controller.WindowManager.show_recovery()

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

        self.encryption_algorithm = QComboBox()
        self.encryption_algorithm.addItem("AES-128")
        self.encryption_algorithm.addItem("AES-192")
        self.encryption_algorithm.addItem("AES-256")
        self.encryption_algorithm.addItem("SM4")
        self.encryption_algorithm.setCurrentIndex(1)

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
        form_layout.addRow("加密算法:", self.encryption_algorithm)

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

        if '@' in username:
            errors.append(f"'{username}'中不得含有“@”")

        # 验证邮箱格式
        if email and not re.match(r'^[\w\.-]+@[\w-]+\.[\w\.-]+$', email):
            errors.append("邮箱格式不正确")

        # 验证密码一致性
        if password and repeat_password and password != repeat_password:
            errors.append("两次输入的密码不一致")

        # 显示结果
        if errors:
            QMessageBox.critical(self, "输入错误", "\n".join(errors))

        if not errors:
            try:
                # 生成加盐哈希密码
                salt = os.urandom(32)
                key = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    salt,
                    100000
                )
                password_hash = f"{salt.hex()}:{key.hex()}"

                # 执行数据库操作
                with Database.Courier.MariaDBCourier(Database.Gatekeeper.load_config()) as courier:
                    if courier.reg_new_user(username, password_hash, email):
                        QMessageBox.information(self, "成功", "注册成功")
                        self.close()
                        Core.Controller.WindowManager.show_login()
                    else:
                        QMessageBox.critical(self, "错误", "用户名或邮箱已存在")
            except Exception as e:
                QMessageBox.critical(self, "系统错误", f"数据库连接失败: {str(e)}")







class AboutWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QGridLayout(central_widget)

        self.button_about_Qt= QtWidgets.QPushButton("About Qt")
        layout.addWidget(self.button_about_Qt, 0, 0)


class LoginThread(QtCore.QThread):
    result_signal = QtCore.Signal(object)

    def __init__(self, identifier, password):
        super().__init__()
        self.identifier = identifier
        self.password = password

    def run(self):

        try:
            with Database.Courier.MariaDBCourier(Database.Gatekeeper.load_config()) as courier:
                # 确定查询字段
                is_email = "@" in self.identifier
                field = "email" if is_email else "username"

                # 参数化查询
                query = f"""
                    SELECT 
                        id, 
                        password_hash,
                        username 
                    FROM users 
                    WHERE {field} = %s
                """

                # 执行查询
                user_data = courier.execute_query(
                    query,
                    (self.identifier,),
                    fetch_all=False
                )

                if not user_data:
                    Log.LoginLogger.login_error_log("[AUTH] 用户不存在")
                    self.result_signal.emit(False)
                    return

                user_id, stored_hash, username = user_data


                # 密码验证
                if ":" in stored_hash:  # PBKDF2
                    salt_hex, key_hex = stored_hash.split(":")
                    salt = bytes.fromhex(salt_hex)

                    new_key = hashlib.pbkdf2_hmac(
                        'sha256',
                        self.password.encode(),
                        salt,
                        100000
                    ).hex()

                    is_valid = (new_key == key_hex)
                else:  # 兼容旧版SHA256
                    current_hash = hashlib.sha256(
                        self.password.encode()
                    ).hexdigest()
                    is_valid = (current_hash == stored_hash)

                Log.LoginLogger.login_info_log(f"[AUTH] 用户 {username} 尝试登录，密码验证结果：{is_valid}")
                self.result_signal.emit(is_valid)

        except Exception as e:
            Log.LoginLogger.login_error_log(f"[AUTH 错误] {str(e)}")
            self.result_signal.emit(e)
