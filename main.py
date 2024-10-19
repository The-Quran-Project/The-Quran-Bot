import os

from dotenv import load_dotenv

from bot import startBot
from bot.utils import runFlask
from bot.utils import startLogger
from bot.utils import checkVersion
from bot.utils import getArguments


load_dotenv()
ARGS = getArguments()
LOCAL = os.environ.get("LOCAL") or ARGS.ARG_LOCAL
STOP_FLASK = os.environ.get("STOP_FLASK") or ARGS.ARG_STOP_FLASK

if __name__ == "__main__":
    if not LOCAL and not STOP_FLASK:
        runFlask()

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
