from datetime import datetime

import httpx, time
import multiprocessing

from bot import startBot




renderUrl = "https://quran-bot-2i9n.onrender.com/"
def check():
    while 1:
        try:
            r = httpx.get(renderUrl, timeout=30, follow_redirects=1).status_code
        except:r=404
        print(f"\nStatus {r} at: {datetime.now()}", end="\r")
        time.sleep(13)



if __name__ == "__main__":
    # multiprocessing.Process(target=check).start()
    startBot()