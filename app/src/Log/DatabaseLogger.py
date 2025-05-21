import logging

logger = logging.getLogger("SetupLogger")
# logger.setLevel(level=logging.INFO)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("./log/db.log")
# handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Transcript
"""

def db_info_log(text):
    logger.info(text)

def db_error_log(text):
    logger.error(text)

def db_debug_log(text):
    logger.debug(text)

def db_warning_log(text):
    logger.warning(text)
