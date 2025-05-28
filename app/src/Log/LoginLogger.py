import logging

logger = logging.getLogger("SetupLogger")
logger.setLevel(level=logging.INFO)

handler = logging.FileHandler("./log/login.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Transcript
"""

def login_info_log(text):
    logger.info(text)

def login_error_log(text):
    logger.error(text)

def user_key_generation_log(user:str):
    logger.info(user + "已新建密钥对")