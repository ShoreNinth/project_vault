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

def mkdir_success(dir):
    logger.info(dir+"mkdir success!")

def mkdir_failure(dir, reason):
    logger.error(dir+"mkdir failure! "+reason)

def mkdir_skipped(dir):
    logger.info(dir+"mkdir skipped.")

"""
Makefile
"""

def makefile_success(file):
    logger.info(file+"makefile success!")

def makefile_failure(file, reason):
    logger.error(file+"makefile failure! "+reason)

