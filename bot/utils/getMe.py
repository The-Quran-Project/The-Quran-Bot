import httpx
import time

from datetime import datetime


renderUrl = "https://quran-bot-2i9n.onrender.com/"


class Counter:
    count = 1


def checkOnInterval(sec: int = 5):
    while 1:
        try:
            r = httpx.get(renderUrl, timeout=None, follow_redirects=1).status_code
        except:
            r = 404

        if Counter.count % 10 == 0:
            print(f"\nStatus Code: {r} @ {datetime.now():%d-%m-%y %H:%M:%S}\n")

        Counter.count += 1
        time.sleep(sec)
