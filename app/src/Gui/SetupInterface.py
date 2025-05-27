import mariadb
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                               QLineEdit, QLabel, QPushButton, QTextEdit,
                               QMessageBox, QGroupBox, QCheckBox)
from PySide6.QtGui import QColor, QPalette, QClipboard
from PySide6.QtCore import Qt, Signal


from Config.DBConfig import DBConfig
import Database.Courier
import Database.Gatekeeper
import Log.SetupLogger


class DatabaseSetupWindow(QMainWindow):
    operation_complete = Signal(bool, str)  # 操作结果信号

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
        self.setWindowTitle("数据库初始化")
        self.setFixedSize(800, 600)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QGridLayout(main_widget)

        # 步骤1：Root认证
        root_group = QGroupBox("步骤1: Root认证")
        root_layout = QGridLayout(root_group)
        self.root_host = QLineEdit("localhost")
        self.root_port = QLineEdit("3306")
        self.root_user = QLineEdit("root")
        self.root_password = QLineEdit()
        self.root_password.setEchoMode(QLineEdit.Password)
        self.root_connect_btn = QPushButton("连接")
        self.root_connect_btn.clicked.connect(self.connect_root)

        root_layout.addWidget(QLabel("主机:"), 0, 0)
        root_layout.addWidget(self.root_host, 0, 1)
        root_layout.addWidget(QLabel("端口:"), 1, 0)
        root_layout.addWidget(self.root_port, 1, 1)
        root_layout.addWidget(QLabel("用户:"), 2, 0)
        root_layout.addWidget(self.root_user, 2, 1)
        root_layout.addWidget(QLabel("密码:"), 3, 0)
        root_layout.addWidget(self.root_password, 3, 1)
        root_layout.addWidget(self.root_connect_btn, 4, 1)
        layout.addWidget(root_group, 0, 0, 1, 2)

        # 步骤2：创建配置
        config_group = QGroupBox("步骤2: 创建新用户和数据库")
        config_layout = QGridLayout(config_group)

        # 新用户配置
        self.new_user = QLineEdit()
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.password_strength = QLabel("密码强度: ")

        self.new_password.textChanged.connect(self.check_password_strength)
        self.update_strength_label("弱", QColor(255, 0, 0))

        config_layout.addWidget(QLabel("新用户名:"), 0, 0)
        config_layout.addWidget(self.new_user, 0, 1)
        config_layout.addWidget(QLabel("密码:"), 1, 0)
        config_layout.addWidget(self.new_password, 1, 1)
        config_layout.addWidget(QLabel("确认密码:"), 2, 0)
        config_layout.addWidget(self.confirm_password, 2, 1)
        config_layout.addWidget(self.password_strength, 2, 2)
        layout.addWidget(config_group, 1, 0, 1, 2)

        # 步骤3：执行
        self.execute_btn = QPushButton("执行初始化")
        self.execute_btn.clicked.connect(self.execute_initialization)
        self.execute_btn.setEnabled(False)
        layout.addWidget(self.execute_btn, 2, 1)

        # 状态显示
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        layout.addWidget(self.status_output, 3, 0, 1, 2)

        # 连接状态
        self.root_conn = None
        self.operation_complete.connect(self.handle_result)

    def connect_root(self):
        """连接root账户"""
        try:
            conn = mariadb.connect(
                user=self.root_user.text().strip(),
                password=self.root_password.text(),
                host=self.root_host.text().strip(),
                port=int(self.root_port.text()),
                database=None
            )
            self.root_conn = conn
            self.status_output.append("√ 成功连接到MariaDB服务器")
            self.execute_btn.setEnabled(True)
        except mariadb.Error as e:
            self.show_error(f"连接失败: {str(e)}")
            self.root_conn = None
            self.execute_btn.setEnabled(False)

    def validate_config(self):
        """验证新用户配置"""
        errors = []
        user = self.new_user.text().strip()
        pwd = self.new_password.text()
        confirm = self.confirm_password.text()

        # 保留用户名检查
        if user in self.RESERVED_USERNAMES:
            errors.append(f"'{user}'是系统保留用户名，请输入合法用户名")

        if not user:
            errors.append("用户名不能为空")
        if not pwd:
            errors.append("密码不能为空")
        if pwd != confirm:
            errors.append("两次输入的密码不一致")

        # ASCII字符检查
        if not re.match(r'^[\x00-\x7F]+$', user):
            errors.append("用户名包含非ASCII字符")
        if not re.match(r'^[\x00-\x7F]+$', pwd):
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

    def execute_initialization(self):
        """执行初始化操作"""
        if not self.root_conn:
            self.show_error("未连接到数据库")
            return

        # 验证输入
        errors = self.validate_config()
        if errors:
            self.show_error("\n".join(errors))
            return

        try:
            cursor = self.root_conn.cursor()
            user = self.new_user.text().strip()
            pwd = self.new_password.text()

            # 创建数据库
            self.status_output.append("▶ 创建数据库 project_vault...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS project_vault "
                           "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            Log.SetupLogger.setup_info_log("▶ 创建数据库 project_vault...")

            # 创建用户
            self.status_output.append(f"▶ 创建用户 {user}...")
            cursor.execute(f"CREATE USER IF NOT EXISTS ?@'localhost' IDENTIFIED BY ?",
                           (user, pwd))
            Log.SetupLogger.setup_info_log(f"▶ 创建用户 {user}...")

            # 授予权限
            privileges = "ALL PRIVILEGES"
            self.status_output.append(f"▶ 授予 {privileges} 权限...")
            cursor.execute(f"GRANT {privileges} ON project_vault.* TO ?@'localhost'", (user,))
            Log.SetupLogger.setup_info_log(f"▶ 授予 {privileges} 权限...")

            self.root_conn.commit()

            # 更新全局配置
            new_config = {
                'user': user,
                'password': pwd,
                'host': self.root_host.text().strip(),
                'port': int(self.root_port.text()),
                'database': 'project_vault'
            }

            DBConfig.update_config(new_config)
            # 数据库密码持久化
            Database.Gatekeeper.save_config(new_config)

            with Database.Courier.MariaDBCourier(DBConfig.get_config()) as courier:

                # 初始化表结构
                courier.initialize_vault_tables()

            self.operation_complete.emit(True, "初始化成功完成！")
            Log.SetupLogger.setup_info_log("初始化成功完成！")

        except mariadb.Error as e:
            self.root_conn.rollback()
            self.operation_complete.emit(False, f"操作失败: {str(e)}")
            Log.SetupLogger.setup_error_log(f"操作失败: {str(e)}")

    def handle_result(self, success, message):
        """处理操作结果"""
        if success:
            self.status_output.append(f"✓ {message}")
            QMessageBox.information(self, "成功", message)
        else:
            self.status_output.append(f"✗ {message}")
            QMessageBox.critical(self, "错误", message)

    def show_error(self, message):
        """显示错误"""
        QMessageBox.critical(self, "输入错误", message)

