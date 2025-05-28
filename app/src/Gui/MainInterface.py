from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QDateTime
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QFileDialog, QLineEdit, \
    QListWidget, QListWidgetItem, QStackedWidget, QScrollArea, QApplication, QMessageBox


# 数据模型
class RecoveryCode:
    def __init__(self, code, used=False):
        self.code = code
        self.used = used


class ServiceAccount:

    def __init__(self, name, issuer, codes):

        self.name = name
        self.issuer = issuer
        self.codes = [RecoveryCode(code) for code in codes]
        self.last_used = None  # 新增最后使用时间字段


# 自定义列表项组件
class EntryWidget(QWidget):
    clicked = Signal()

    def __init__(self, account):
        super().__init__()
        self.account = account
        self.init_ui()
        self.status_label = QLabel(f"剩余恢复码: ...")

    def init_ui(self):
        layout = QHBoxLayout()

        # 服务图标
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(":/icons/pv.png").pixmap(32, 32))
        layout.addWidget(icon_label)

        # 信息区域
        info_layout = QVBoxLayout()
        title = QLabel(f"<b>{self.account.name}</b> ({self.account.issuer})")
        title.setStyleSheet("font-size: 14px; color: #2c3e50;")
        info_layout.addWidget(title)

        codes_left = len([c for c in self.account.codes if not c.used])
        status = QLabel(f"剩余恢复码: {codes_left}/{len(self.account.codes)} | 最后使用: 从未使用")
        status.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        info_layout.addWidget(status)

        layout.addLayout(info_layout)

        # 操作按钮
        btn_layout = QVBoxLayout()
        show_btn = QPushButton("显示")
        show_btn.setFixedWidth(80)
        show_btn.clicked.connect(self.clicked)
        btn_layout.addWidget(show_btn)

        copy_btn = QPushButton("复制")
        copy_btn.setFixedWidth(80)
        copy_btn.clicked.connect(self.copy_code)
        btn_layout.addWidget(copy_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setStyleSheet("""
            QPushButton { 
                background: #3498db; 
                color: white; 
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover { background: #2980b9; }
        """)

    def copy_code(self):
        # 实际应实现安全复制逻辑
        print(f"复制 {self.account.name} 的恢复码")

    def update_status(self):
        codes_left = len([c for c in self.account.codes if not c.used])
        # 格式化最后使用时间
        last_used = self.account.last_used
        time_str = last_used.toString("yyyy-MM-dd hh:mm:ss") if last_used else "从未使用"

        self.status_label.setText(
            f"剩余恢复码: {codes_left}/{len(self.account.codes)} | 最后使用: {time_str}"
        )


# 主界面
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.init_data()
        self.init_ui()

    # @QtCore.Slot()
    # def get_current_account(self):
    #     return LoginThread.run()

    def init_data(self):
        self.accounts = [
            # ServiceAccount("GitHub", "github.com", ["3F7A-9B2C", "5D8E-1F4A"]),
            ServiceAccount("GitHub", "github.com", ["5D8E-1F4A"]),
            ServiceAccount("Google", "google.com", ["A3B2-C9D1", "E4F5-6G7H"])
        ]

    def init_ui(self):
        self.setWindowTitle("安全恢复码保险箱")
        self.setMinimumSize(1280, 720)

        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧导航
        left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(left_sidebar)

        # 中央列表
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 1)

        # 右侧详情
        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel)

        self.setCentralWidget(main_widget)
        self.apply_styles()
        self.lock_timer = QTimer()
        self.lock_timer.setSingleShot(True)  # 设置为单次触发
        self.lock_timer.timeout.connect(self.show_exit_warning)
        self.reset_lock_timer()

    def create_left_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 安全状态
        # current_user = LoginThread.run
        # user_logined = QLabel(f"欢迎回来，{LoginThread.run.userdata}!")
        security_status = QLabel("🔒 安全锁定中\n最后活动：2分钟前")
        security_status.setStyleSheet("""
            background: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
        """)
        layout.addWidget(security_status)

        # 分类过滤
        # filter_layout = QVBoxLayout()
        # filter_layout.addWidget(QLabel("分类筛选："))
        # categories = ["⭐ 所有账户", "💻 工作账户", "🛒 购物账户"]
        # for cat in categories:
        #     btn = QPushButton(cat)
        #     btn.setCheckable(True)
        #     btn.setStyleSheet("""
        #         QPushButton {
        #             text-align: left;
        #             padding: 10px;
        #             border-radius: 4px;
        #         }
        #         QPushButton:checked { background: #3498db; color: white; }
        #     """)
        #     filter_layout.addWidget(btn)
        # layout.addLayout(filter_layout)

        # 快速操作
        quick_actions = QVBoxLayout()
        quick_actions.addWidget(QLabel("快速操作："))
        button_shamir = QPushButton("📤 开始分片")

        button_import = QPushButton("📥 导入文件")
        # button_import.clicked.connect(QFileDialog())
        button_shamir.setStyleSheet("text-align: left; padding: 10px;")
        button_import.setStyleSheet("text-align: left; padding: 10px;")

        quick_actions.addWidget(button_shamir)
        quick_actions.addWidget(button_import)

        # actions = ["🔄 立即同步", "📤 导出备份", "⚙️ 设置"]
        # for action in actions:
        #     btn = QPushButton(action)
        #     btn.setStyleSheet("text-align: left; padding: 10px;")
        #     quick_actions.addWidget(btn)

        layout.addLayout(quick_actions)

        sidebar.setLayout(layout)
        return sidebar

    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # 搜索栏
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("搜索账户...")
        search_bar.setClearButtonEnabled(True)
        search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(search_bar)

        # 条目列表
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.populate_list()
        layout.addWidget(self.list_widget)

        panel.setLayout(layout)
        return panel

    def populate_list(self):
        # 清空现有条目（关键修复）
        self.list_widget.clear()

        for account in self.accounts:
            item = QListWidgetItem()
            widget = EntryWidget(account)
            widget.clicked.connect(self.show_details)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def create_right_panel(self):
        panel = QWidget()
        panel.setFixedWidth(360)
        self.stacked_widget = QStackedWidget()

        # 未认证面板
        auth_panel = QWidget()
        auth_layout = QVBoxLayout()
        auth_layout.addWidget(QLabel("⚠️ 需要身份验证才能显示"))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入主密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.password_input)

        bio_btn = QPushButton("验证")
        bio_btn.clicked.connect(self.authenticate)
        auth_layout.addWidget(bio_btn)

        auth_panel.setLayout(auth_layout)

        # 详情面板
        self.detail_panel = self.create_detail_panel()

        self.stacked_widget.addWidget(auth_panel)
        self.stacked_widget.addWidget(self.detail_panel)

        panel_layout = QVBoxLayout()
        panel_layout.addWidget(self.stacked_widget)
        panel.setLayout(panel_layout)
        return panel

    def create_detail_panel(self):
        scroll = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout()

        # 服务信息
        self.service_title = QLabel()
        self.service_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.service_title)

        # 二维码
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)

        # 恢复码列表
        self.code_list = QListWidget()
        layout.addWidget(QLabel("恢复码："))
        layout.addWidget(self.code_list)

        # 安全提示
        tip = QLabel("⚠️ 复制后剪贴板将在15秒后自动清除")
        tip.setStyleSheet("color: #e74c3c; font-size: 12px;")
        layout.addWidget(tip)

        content.setLayout(layout)
        scroll.setWidget(content)
        return scroll

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #ecf0f1; }
            QListWidget { 
                background: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
            QScrollArea { border: none; }
        """)

    def authenticate(self):
        # 实际应实现安全验证逻辑
        self.authenticated = True
        self.stacked_widget.setCurrentIndex(1)
        self.update_details(self.accounts[0])

    def show_details(self):
        if self.authenticated:
            # 获取选中条目数据
            current_item = self.list_widget.currentItem()
            if current_item:
                widget = self.list_widget.itemWidget(current_item)
                self.update_details(widget.account)

    def update_details(self, account):
        self.service_title.setText(f"{account.name} ({account.issuer})")
        self.code_list.clear()

        for code in account.codes:
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()

            code_label = QLabel(code.code)
            status_btn = QPushButton("标记已用" if not code.used else "已使用")
            status_btn.setEnabled(not code.used)

            # 绑定点击事件
            status_btn.clicked.connect(
                lambda checked, c=code: self.handle_code_used(c)
            )

            layout.addWidget(code_label)
            layout.addWidget(status_btn)
            widget.setLayout(layout)

            item.setSizeHint(widget.sizeHint())
            self.code_list.addItem(item)
            self.code_list.setItemWidget(item, widget)


        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)

            if widget.account == account:
                widget.update_status()  # 调用更新方法
                break


    def handle_code_used(self, code):
        if not code.used:
            reply = QMessageBox.question(
                self, '确认使用',
                f"确定要标记 {code.code} 为已使用吗？\n此操作不可逆！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                code.used = True
                # 更新账户的最后使用时间
                current_account = self.get_current_selected_account()
                if current_account:
                    current_account.last_used = QDateTime.currentDateTime()  # 记录当前时间

                self.update_details(current_account)
                self.populate_list()

    def get_current_selected_account(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            widget = self.list_widget.itemWidget(current_item)
            return widget.account
        return None



# 安全显示方案（星号切换）
    def toggle_code_visibility(self, index):
        if index.column() == 2:
            current_value = self.model.item(index.row(), 2).text()
            if "•" in current_value:
                real_code = self.decrypt_code(current_value)  # 解密方法需要自行实现
                self.model.setData(index, real_code)
            else:
                self.model.setData(index, "•" * 10)


    # 上下文菜单（右键菜单）
    def contextMenuEvent(self, event):

        menu = QtWidgets.QMenu(self)

        copy_action = menu.addAction("📋 复制恢复码")

        # edit_action = menu.addAction("✏️ 编辑条目")
        #
        # delete_action = menu.addAction("🗑️ 删除条目")

        # 获取当前选中的列表项

        selected_index = self.list_widget.currentIndex()  # 修复点：使用正确的列表控件

        if not selected_index.isValid():
            return

        action = menu.exec(event.globalPos())
        if action == copy_action:

            # 实现安全复制逻辑

            item = self.list_widget.item(selected_index.row())
            widget = self.list_widget.itemWidget(item)
            account = widget.account

            # 获取第一个可用恢复码

            for code in account.codes:
                if not code.used:
                    QApplication.clipboard().setText(code.code)
                    QTimer.singleShot(15000, lambda: QApplication.clipboard().clear())
                    break

        # elif action == edit_action:
        #
        #     # 添加编辑逻辑（需要实现编辑对话框）
        #
        #     print("edit")
        #
        #     pass
        #
        # elif action == delete_action:
        #
        #     # 添加删除逻辑（需要确认对话框）
        #     print("delete")
        #
        #     pass


    # 安全计时锁定
    def reset_lock_timer(self):
        self.lock_timer.start(300000)  # 5分钟无操作自动锁定

    def show_exit_warning(self):

        """显示退出警告对话框"""

        msg_box = QMessageBox(self)

        msg_box.setIcon(QMessageBox.Warning)

        msg_box.setWindowTitle("会话超时")

        msg_box.setText("您已5分钟无操作，即将退出系统")

        msg_box.setInformativeText("确认退出请点击【退出】，继续使用请点击【保持登录】")

        # 创建自定义按钮
        exit_btn = msg_box.addButton("退出", QMessageBox.AcceptRole)
        keep_btn = msg_box.addButton("保持登录", QMessageBox.RejectRole)
        # 显示对话框并等待用户响应

        msg_box.exec()
        if msg_box.clickedButton() == exit_btn:
            self.graceful_exit()
        else:
            self.reset_lock_timer()

    def graceful_exit(self):

        """优雅退出程序"""

        # 1. 保存当前状态（根据需要添加）
        # 2. 关闭所有子窗口
        QtWidgets.QApplication.closeAllWindows()

        # 3. 退出事件循环

        QtWidgets.QApplication.quit()


    # def lock_interface(self):
    #     self.password_dialog = LockScreenDialog()
    #     if self.password_dialog.exec() != QDialog.Accepted:
    #         QApplication.quit()
    #     self.reset_lock_timer()
