import logging

def startLogger(name):
    logger = logging.getLogger(name)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    