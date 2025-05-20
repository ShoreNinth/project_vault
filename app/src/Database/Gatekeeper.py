
import json
import os

from cryptography.fernet import Fernet

CWD = os.getcwd()


CONFIG_PATH = f'{CWD}/config/db_config.enc'
KEY_PATH = f'{CWD}/key/key.key'

def generate_key():
    """生成加密密钥"""
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key

def save_config(config: dict):
    """加密保存配置"""
    if not os.path.exists(KEY_PATH):
        generate_key()

    with open(KEY_PATH, "rb") as f:
        key = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(config).encode())

    with open(CONFIG_PATH, "wb") as f:
        f.write(encrypted)

def load_config() -> dict:
    """解密读取配置"""
    with open(KEY_PATH, "rb") as f:
        key = f.read()

    with open(CONFIG_PATH, "rb") as f:
        encrypted = f.read()

    fernet = Fernet(key)
    return json.loads(fernet.decrypt(encrypted).decode())
