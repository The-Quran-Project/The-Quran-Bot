import logging
from datetime import datetime

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.ERROR)


def getLogger(name: str):
    logger = logging.getLogger(name)

    return logger
