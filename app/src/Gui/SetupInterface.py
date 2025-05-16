import os
import sys
import re

from PySide6 import QtCore
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QLineEdit, QLabel, QPushButton, QTextEdit,
                               QMessageBox, QGridLayout)
from PySide6.QtGui import QClipboard, QColor, QPalette
from PySide6.QtCore import Qt


# os.environ["QT_WAYLAND_SHELL_INTEGRATION"] = "kde-shell"  # 强制 KDE 集成

class DatabaseSetupWindow(QMainWindow):

    # MariaDB系统保留用户名列表
    RESERVED_USERNAMES = [
        'root', 'mysql', 'mariadb.sys',
        'mysql.session', 'mysql.sys',
        'debian-sys-maint', 'mariadb',
        'sys', 'administrator', 'nobody',
        'PUBLIC', 'root'
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据库设置向导")
        self.setFixedSize(600, 500)  # 调整窗口高度

        # 主部件和网格布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QGridLayout(main_widget)

        # 设置列宽比例（重要！）
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)  # 输入框列占3份宽度
        layout.setColumnStretch(2, 1)  # 强度标签列占1份

        # 用户名输入（第0行）
        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1, 1, 2)  # 跨列1-2

        # 密码输入（第1行）
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.password_input, 1, 1, 1, 2)  # 跨列1-2

        # 确认密码输入（第2行）
        self.confirm_password_label = QLabel("确认密码:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_label, 2, 0)
        layout.addWidget(self.confirm_password_input, 2, 1, 1, 2)  # 跨列1-2

        # 密码强度提示（第3行）
        self.password_strength = QLabel("密码强度: ")
        layout.addWidget(self.password_strength, 3, 0, 1, 3)  # 全宽显示

        # 生成SQL按钮（第4行）
        self.generate_sql_button = QPushButton("生成SQL")
        self.generate_sql_button.clicked.connect(self.generate_sql)
        layout.addWidget(self.generate_sql_button, 4, 0, 1, 3)  # 全宽

        # SQL显示框（第5行）
        self.sql_output = QTextEdit()
        self.sql_output.setReadOnly(True)
        layout.addWidget(self.sql_output, 5, 0, 3, 3)  # 跨3列，占3行高度

        # 按钮区域（第8行）
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()

        # 复制按钮
        self.copy_button = QPushButton("复制 SQL")
        self.copy_button.clicked.connect(self.copy_sql_output)
        button_layout.addWidget(self.copy_button)

        # 下一步按钮
        self.next_button = QPushButton("下一步")
        button_layout.addWidget(self.next_button)

        layout.addWidget(button_container, 8, 0, 1, 3)

        self.statusBar().showMessage("就绪")

        # 实时密码强度检查
        self.password_input.textChanged.connect(self.check_password_strength)
        self.update_strength_label("弱", QColor(255, 0, 0))


    def validate_inputs(self):
        """集中验证所有输入"""
        errors = []

        # 获取输入值
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # 保留用户名检查
        if username in self.RESERVED_USERNAMES:
            errors.append(f"'{username}'是系统保留用户名，请输入合法用户名")

        # 非空检查
        if not username:
            errors.append("用户名不能为空")
        if not password:
            errors.append("密码不能为空")
        if not confirm_password:
            errors.append("确认密码不能为空")

        # 如果存在空值直接返回
        if errors:
            return errors

        # 密码一致性检查
        if password != confirm_password:
            errors.append("两次输入的密码不一致")

        # ASCII字符检查
        if not re.match(r'^[\x00-\x7F]+$', username):
            errors.append("用户名包含非ASCII字符")
        if not re.match(r'^[\x00-\x7F]+$', password):
            errors.append("密码包含非ASCII字符")

        return errors

    def check_password_strength(self, password):
        """实时密码强度检查（仅显示不阻止）"""
        strength = self.calculate_password_strength(password)
        if strength == "强":
            color = QColor(12, 255, 121)
        elif strength == "中":
            color = QColor(255, 143, 10)
        else:
            color = QColor(255, 0, 0)
        self.update_strength_label(strength, color)

    def calculate_password_strength(self, password):
        """密码强度计算逻辑"""
        if len(password) < 8:
            return "弱"

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        score = sum([has_upper, has_lower, has_digit, has_special])

        if len(password) >= 9 and score >= 4:
            return "强"
        if len(password) >= 8 and score >= 2:
            return "中"
        return "弱"

    def update_strength_label(self, text, color):
        """更新密码强度标签"""
        palette = self.password_strength.palette()
        palette.setColor(QPalette.WindowText, color)
        self.password_strength.setPalette(palette)
        self.password_strength.setText(f"密码强度: {text}")

    def generate_sql(self):
        """生成SQL代码"""
        # 执行集中验证
        errors = self.validate_inputs()

        if errors:
            self.show_combined_warning(errors)
            return None

        # 获取有效输入
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # 生成SQL
        sql = f"-- 创建用户\n"
        sql += f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';\n\n"
        sql += f"-- 创建数据库\n"
        sql += "CREATE DATABASE IF NOT EXISTS project_vault\n"
        sql += "  CHARACTER SET utf8mb4\n"
        sql += "  COLLATE utf8mb4_unicode_ci;\n\n"
        sql += f"-- 授予权限\n"
        sql += f"GRANT ALL PRIVILEGES ON project_vault.* TO '{username}'@'localhost';\n\n"
        sql += "FLUSH PRIVILEGES;"

        self.sql_output.setPlainText(sql)

    # 修改复制方法
    @QtCore.Slot()
    def copy_sql_output(self):
        clipboard = QApplication.clipboard()
        sql_text = self.sql_output.toPlainText()

        if sql_text:
            clipboard.setText(sql_text)
            self.statusBar().showMessage("SQL已复制到剪贴板", 3000)  # 显示3秒
        else:
            self.statusBar().showMessage("错误：没有可复制的SQL内容", 5000)

    def show_combined_warning(self, messages):
        """显示合并的警告消息"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("输入验证错误")
        msg_box.setText("以下问题需要修正：")
        msg_box.setInformativeText("\n• " + "\n• ".join(messages))
        msg_box.exec()

