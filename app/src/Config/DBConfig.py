# Config/DBConfig.py
class DBConfig:
    _instance = None
    config = {
        'user': None,
        'password': None,
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'project_vault'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def update_config(cls, new_config):
        cls.config.update(new_config)
        # 可选：添加配置加密逻辑
        # cls.config['password'] = encrypt_password(new_config['password'])

    @classmethod
    def get_config(cls):
        # 可选：添加配置解密逻辑
        return cls.config.copy()
