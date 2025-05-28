import base64
import json
import hashlib

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGridLayout,
                               QLineEdit, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

import Security.Crypto
import Security.SSS
from cryptography.hazmat.primitives import serialization
import os
from base64 import b64decode

import base64


def load_aes_key_bytes(key_path: str) -> bytes:

    """
    加载AES密钥文件并返回原始字节数据
    :param key_path: 密钥文件路径（支持任意二进制格式）
    :return: AES密钥的原始字节数据
    """
    try:
        with open(key_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"密钥文件未找到：{os.path.abspath(key_path)}")
    except Exception as e:
        raise RuntimeError(f"读取密钥文件失败：{str(e)}") from e


def load_secret(secret_str: str) -> bytes:
    """
    完整Base64解码（处理填充和特殊字符）
    :param secret_str: 原始Base64字符串
    :return: 解码后的原始字节
    """
    # 补全填充符
    missing_padding = len(secret_str) % 4
    if missing_padding:
        secret_str += '=' * (4 - missing_padding)

    # 处理URL安全格式（可选）
    secret_str = secret_str.replace('-', '+').replace('_', '/')

    try:
        return base64.b64decode(secret_str, validate=True)
    except Exception as e:
        raise ValueError(f"Base64解码失败：{str(e)}") from e

def load_private_key_bytes(key_path: str) -> bytes:
    """
    增强版PEM加载器（支持加密私钥检测）
    :return: 原始私钥DER字节
    """
    with open(key_path, "rb") as f:
        pem_data = f.read().decode('utf-8', errors='ignore')  # 容忍非UTF-8字符

    # 检测加密私钥
    if 'ENCRYPTED' in pem_data:
        raise ValueError("检测到加密私钥，请先解密！")

    # 增强型PEM解析
    pem_lines = pem_data.split('\n')
    body_lines = []
    in_body = False

    for line in pem_lines:
        if line.startswith('-----BEGIN ') and 'PRIVATE KEY' in line:
            in_body = True
            continue
        if line.startswith('-----END '):
            in_body = False
            continue
        if in_body and line.strip():
            body_lines.append(line.strip())

    if not body_lines:
        raise ValueError("未找到有效的PEM主体数据")

    # 严格Base64解码（添加填充符）
    base64_data = ''.join(body_lines)
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)

    try:
        raw_bytes = base64.b64decode(base64_data, validate=True)
    except Exception as e:
        raise ValueError(f"Base64解码失败：{str(e)}") from e

    return raw_bytes

def split_private_key_bytes(secret: bytes) -> bytes:
    # 使用 secp256k1 的阶作为素数 p
    # p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    # p太小了
    print("原秘密：",secret)

    p=420980254453935008154505624481442383441615288088445880985778480721118366200529297662844223875542909878193618383615603475713639264410350373698151412688347944499416741772515069793024550389858263257671132201850967093794635420934592902972252186204604501778542125108222467602496485109294886014106398808705549529824677784747748837884875071005873927577874198472525645674931317724199867860136095632404788376205994229901216339433987568263008103029350627815366016290240983353580057456878680727890686653353313452946297864991916453905705716329261607785145363724798622186541388981272943093285082113942908496023426820951717367975656864826992215938211996700694216838727282673229236432056368929184843775049855990573967476101945368510067410822466881297597557578839817562098827589416924567376251351377861868976455618293542511085042936831850968299002562960903081650307671493771637192147193849547550575629110750111482211453228748747015746147310985184740137153138125287805665634047825666658596731658983057554294073292401585663430738516013985378090545960125427844650842568345827240482672182385730597435782404105447689154663779212990916564753208475671335811065948373309633034156969539012525157147378909560734480194711117232059511791763926112655525863809004431462057178809000875304767958713273626314935133195374134848664124582132104816905400966153302935680745261186147748799608398856044204857793004948099184383671954836450169044196468960997333602201318239870095894207912274670170153174670398937935693964721647597830265393894699525847698522600474844368147283941304989493641086617222208756300091556969039543433430369924600120741145170194638069555002206023954884092116093649788924279
    n = 5
    k = 3

    # 分片生成
    shares = Security.SSS.split_secret(secret, n, k, p)

    # for share in shares:
    #     print(json.dumps(share, indent=2))
    return shares



def reconstruct_secret(secret:bytes, p , shares):
    # 模拟恢复（使用前3个分片）
    recovered_secret = Security.SSS.recover_secret(shares[:3], p, 3)
    print("\nRecovered secret:", recovered_secret)

    if recovered_secret == secret:
        print("Successfully recovered")
    else:
        print("Failed to recovered")

def safe_b64encode(data: bytes) -> str:
    """生成标准化Base64字符串"""
    encoded = base64.b64encode(data)
    # 补全填充符并移除换行符
    return encoded.decode('utf-8').rstrip('=\n') + '=' * (-len(encoded) % 4)

def safe_b64decode(encoded: str) -> bytes:
    """解码标准化Base64字符串"""
    # 补全填充符
    padding = '=' * (-len(encoded) % 4)
    return base64.b64decode(encoded + padding)


class RecoveryUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shamir秘密重构工具")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 输入说明标签
        instr_label = QLabel("请输入至少3个分片（格式：x-y）:")
        instr_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instr_label)

        # 分片输入区域
        grid = QGridLayout()
        self.share_edits = []
        for i in range(5):
            label = QLabel(f"分片 {i + 1}:")
            edit = QLineEdit()
            edit.setPlaceholderText("格式：x-y（例如 3-12345）")
            self.share_edits.append(edit)
            grid.addWidget(label, i, 0)
            grid.addWidget(edit, i, 1)

        main_layout.addLayout(grid)

        # 确认按钮
        self.btn = QPushButton("重构秘密")
        self.btn.clicked.connect(reconstruct_secret)
        self.btn.setStyleSheet("font-size: 16px; padding: 8px;")
        main_layout.addWidget(self.btn, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
