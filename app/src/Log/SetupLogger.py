import logging

logger = logging.getLogger("SetupLogger")
logger.setLevel(level=logging.INFO)

handler = logging.FileHandler("./log/setup.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Start
"""
def start_setup():
    logger.info("Starting Setup")


"""
Mkdir
"""

def mkdir_success(dir_name):
    logger.info(dir_name + "mkdir success!")

def mkdir_failure(dir_name, reason):
    logger.error(dir_name + "mkdir failure! " + reason)

def mkdir_skipped(dir_name):
    logger.info("skipped mkdir: " + dir_name)

"""
Makefile
"""

def makefile_success(file):
    logger.info(file+"makefile success!")

def makefile_failure(file, reason):
    logger.error(file+"makefile failure! "+reason)

"""
Transcript
"""

def setup_info_log(text):
    logger.info(text)

def setup_error_log(text):
    logger.error(text)

