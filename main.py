import os

from dotenv import load_dotenv

from bot import startBot
from bot.utils import runFlask
from bot.utils import startLogger
from bot.utils import checkVersion

load_dotenv()

LOCAL = os.environ.get("LOCAL")


if __name__ == "__main__":
    # if not LOCAL:
    #     runFlask()

    checkVersion()
    startLogger(__name__)

    # Infinite loop to restart the bot in case of any errors
    while 1:
        try:
            startBot()
        except KeyboardInterrupt:
            if LOCAL:
                break
        except Exception as e:
            if LOCAL:
                raise e

            print("Error:", e)
