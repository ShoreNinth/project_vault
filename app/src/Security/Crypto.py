# 处理密钥生成、分片算法和恢复逻辑。
# 功能点：
# RSA 密钥对生成：使用安全库（如 cryptography）生成符合标准的密钥对。
import base64
import hashlib
import os
import gmssl
from cryptography.exceptions import InvalidKey, UnsupportedAlgorithm

import Log.LoginLogger

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

CWD = os.getcwd()

PUBLIC_KEY_PATH = f'{CWD}/key/key.pub'
PRIVATE_KEY_PATH = f'{CWD}/key/key'



class Hash:

    def generate_password_hash(password: str) -> str:
        salt = Fernet.generate_key()
        # 设定一个password，接着使用PBKDF2HMAC。
        # 它是个密钥推导函数，通过多次对salt进行hash运算从而产生密钥。
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        ).hex()

class Symmetric:


    def aes_encryption(self):
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


    def sm4_encryption(self):
        pass





class Asymmetric:

    @staticmethod
    def rsa_keygen(user: str):

        """生成并保存RSA密钥对到指定路径"""

        try:

            os.makedirs(os.path.dirname(PRIVATE_KEY_PATH), exist_ok=True)

            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=1024,
                backend=default_backend(),
            )

            # 序列化私钥（PKCS8格式，无加密）
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            # 保存私钥
            with open(PRIVATE_KEY_PATH, "wb") as f:
                f.write(private_pem)

            # 生成公钥
            public_key = private_key.public_key()
            # 序列化公钥（SubjectPublicKeyInfo格式）
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # 保存公钥
            with open(PUBLIC_KEY_PATH, "wb") as f:
                f.write(public_pem)

            # 记录日志
            Log.LoginLogger.user_key_generation_log(user)
            return True


        except Exception as e:
            Log.LoginLogger.user_key_generation_log(f"密钥生成失败: {str(e)}")
            return False

    @staticmethod
    def load_public_key():
        """从文件系统加载公钥"""
        try:
            with open(PUBLIC_KEY_PATH, "rb") as key_file:
                return serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"公钥文件未找到：{PUBLIC_KEY_PATH}")
        except Exception as e:
            raise RuntimeError(f"公钥加载失败：{str(e)}") from e

    @staticmethod
    def load_private_key():
        """从文件系统加载私钥"""
        try:
            with open(PRIVATE_KEY_PATH, "rb") as key_file:
                return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,  # 与密钥生成时的加密设置保持一致
                    backend=default_backend()
                )
        except FileNotFoundError:
            raise FileNotFoundError(f"私钥文件未找到：{PRIVATE_KEY_PATH}")
        except Exception as e:
            raise RuntimeError(f"私钥加载失败：{str(e)}") from e

    @staticmethod
    def rsa_encryption(msg: str) -> bytes:
        """
        RSA加密方法
        :param msg: 要加密的明文消息（字符串）
        :return: 加密后的密文（字节）
        """
        try:
            public_key = Asymmetric.load_public_key()
            encrypted = public_key.encrypt(
                msg.encode('utf-8'),  # 字符串转字节
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return encrypted
        except (UnsupportedAlgorithm, InvalidKey) as e:
            raise ValueError("加密失败：密钥或填充参数不正确") from e


    @staticmethod
    def rsa_decryption(encrypted_data: bytes) -> str:
        """
        RSA解密方法
        :param encrypted_data: 要解密的密文（字节）
        :return: 解密后的明文（字符串）
        """
        try:
            private_key = Asymmetric.load_private_key()
            decrypted = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode('utf-8')  # 字节转字符串
        except (UnsupportedAlgorithm, InvalidKey) as e:
            raise ValueError("解密失败：密钥或填充参数不正确") from e


class Coding:
    @staticmethod
    def cipher_encode(cipher: bytes) -> str:

        cipher_b64 = base64.b64encode(cipher).decode('utf-8')  # 转字符串

        return cipher_b64

    @staticmethod
    def cipher_decode(cipher_b64: bytes) -> str:

        # 解密前需先Base64解码
        cipher_bytes_restored = base64.b64decode(cipher_b64).decode('utf-8')

        return cipher_bytes_restored
