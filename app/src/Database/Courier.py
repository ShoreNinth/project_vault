# MariaDB Courier
# MariaDB 信使

import mariadb
import sys
from typing import Optional, Union, List, Dict, Any

import Log.DatabaseLogger


class MariaDBCourier:
    """一个更完善的MariaDB数据库操作类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化数据库连接

        :param config: 数据库配置字典，包含以下键:
            - user: 用户名
            - password: 密码
            - host: 主机地址
            - port: 端口号
            - database: 数据库名
            - autocommit: 是否自动提交(默认为False)
        """
        self._conn = None
        self._config = config

    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()

    def connect(self) -> None:
        """建立数据库连接"""
        if self._conn is None:
            try:
                self._conn = mariadb.connect(**self._config)
                Log.DatabaseLogger.info_log("Successfully connected to MariaDB")
            except mariadb.Error as e:
                Log.DatabaseLogger.error_log(f"Error connecting to MariaDB: {e}")
                sys.exit(1)

    @property
    def connection(self) -> mariadb.Connection:
        """获取连接对象"""
        if self._conn is None:
            self.connect()
        return self._conn

    @property
    def cursor(self) -> mariadb.Cursor:
        """获取游标对象"""
        return self.connection.cursor()


    def execute_query(self, query: str, params: Optional[tuple] = None,
                      fetch_all: bool = True) -> Union[List[tuple], int, None]:
        """
        执行SQL查询

        :param query: SQL语句
        :param params: 参数元组
        :param fetch_all: 是否获取所有结果
        :return: 查询结果或影响的行数
        """
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith(('SELECT', 'SHOW')):
                return self.cursor.fetchall() if fetch_all else self.cursor.fetchone()
            else:
                return self.cursor.rowcount
        except mariadb.Error as e:
            Log.DatabaseLogger.error_log(f"Error executing query: {e}")
            return None

    def create_table(self, table_name: str, schema: str) -> bool:
        """
        创建数据表

        :param table_name: 表名
        :param schema: 表结构定义SQL
        :return: 是否创建成功
        """
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            self.connection.commit()

            Log.DatabaseLogger.info_log(f"Table {table_name} created")
            return True
        except mariadb.Error as e:
            Log.DatabaseLogger.error_log(f"Error creating table: {e}")
            self.connection.rollback()
            return False

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            Log.DatabaseLogger.info_log("Successfully closed MariaDB")

    # 示例方法: 创建项目所需的表
    def initialize_vault_tables(self) -> bool:
        """初始化项目所需的表结构"""
        tables = {
            'users': """
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """,
            'tokens': """
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token_name VARCHAR(50) NOT NULL,
                token_value VARCHAR(255) NOT NULL,
                algorithm VARCHAR(20) DEFAULT 'SHA1',
                digits INT DEFAULT 6,
                period INT DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, token_name)
            """
        }

        success = True
        for table_name, schema in tables.items():
            if not self.create_table(table_name, schema):
                success = False

        return success

