from dotenv import load_dotenv

import os
import multiprocessing

from bot import startBot
from bot.utils.getMe import checkOnInterval


load_dotenv()
LOCAL = os.environ.get("LOCAL")


if __name__ == "__main__":
    multiprocessing.Process(target=checkOnInterval).start()

    # Never Stop in Production! :3
    while 1:
        try:
            startBot()
        except KeyboardInterrupt:
            if LOCAL:
                break
        except Exception as e:
            if LOCAL:
                raise e
            if LOCAL:
                break
