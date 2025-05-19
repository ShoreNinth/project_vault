import logging

logger = logging.getLogger("SetupLogger")
logger.setLevel(level=logging.INFO)

handler = logging.FileHandler("./log/db.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


