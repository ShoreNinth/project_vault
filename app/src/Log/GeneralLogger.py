import logging

logger = logging.getLogger("SetupLogger")
logger.setLevel(level=logging.INFO)

handler = logging.FileHandler("./log/general.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Transcript
"""

def general_info_log(text):
    logger.info(text)

def general_error_log(text):
    logger.error(text)

