from dotenv import load_dotenv

import os
import sys
import multiprocessing

from bot import startBot
from bot.utils.getMe import checkOnInterval


load_dotenv()
LOCAL = os.environ.get("LOCAL")


if __name__ == "__main__":
    if sys.version_info < (3, 12):
        print("", "-" * 33, sep="\n")
        print(f"{'Warning':*^33}")
        print("-" * 33, "", sep="\n")

        print("This bot should run on Python 3.12 | Some features may not work on older versions")
        print("You are running Python {}.{} | Consider upgrading".format(sys.version_info[0], sys.version_info[1]))
        
        print("", "-" * 33, "-" * 33, "", sep="\n")

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
            
            print("Error:", e)
