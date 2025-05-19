# 处理密钥生成、分片算法和恢复逻辑。
# 功能点：
# RSA 密钥对生成：使用安全库（如 cryptography）生成符合标准的密钥对。
import cryptography
import gmssl
# 升级密码哈希算法
import hashlib
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

class HashManager:

    def generate_password_hash(password: str) -> str:
        salt = Fernet.generate_key()
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        ).hex()


class AESSolution:

    def AES_encryption(self):
        pass


    # 密码
    password = b"password"
    # 盐
    salt = b"salt"

    # 创建PBKDF2HMAC对象
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    # 派生密钥
    key = kdf.derive(password)




class SM4Solution:

    def SM4_encryption(self):
        pass


