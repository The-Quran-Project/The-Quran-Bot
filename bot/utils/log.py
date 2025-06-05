import logging
from datetime import datetime

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.ERROR)


def getLogger(name: str):
    logger = logging.getLogger(name)

    def dump(data: any):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.txt"
        content = str(data)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    # Attach the dump function to the logger instance
    logger.dump = dump
    return logger
