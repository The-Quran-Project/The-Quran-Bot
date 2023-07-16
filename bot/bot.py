# pylint:disable=W0401
# pylint:disable=W0621
import flask

from telegram import *
from telegram.ext import *
from dotenv import load_dotenv


import os
import time
import logging
import threading

from .handlers import *

load_dotenv()


# Environment Variables
TOKEN = os.environ.get("TOKEN")
IS_LOCAL = os.environ.get("LOCAL")

if IS_LOCAL:
    TOKEN = os.environ.get("TEST")
    print("-" * 27)
    print("Running on local test Bot")
    print("-" * 27)


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)


# Flask app for keeping the bot running in hosted server.
start = time.time()

def secondsToTime(s):
  m, s = divmod(s, 60)
  h, m = divmod(m, 60)
  d, h = divmod(h, 24)
  m = int(m)
  s = int(s)
  h = int(m)
  d = int(d)
  
  result = ""
  if d > 0:
    result += f"{d} day{'s' if d > 1 else ''}"
  if h > 0:
    result += f" {h} hour{'s' if h > 1 else ''}"
  if m > 0:
    result += f" {m} minute{'s' if m > 1 else ''}"
  if not result:
    result = "0 minutes"
  return result.strip()

def runFlask():
    app = flask.Flask("Quran Bot")

    @app.route('/')
    def index():
        return f"<h1>Running for {secondsToTime(time.time()-start)}</h1>"

    app.run("0.0.0.0", 8080)


def runBot():
    if not IS_LOCAL:
        threading.Thread(target=runFlask).start()

    df = Defaults(parse_mode=constants.ParseMode.HTML,
                  block=False, disable_web_page_preview=False)

    bot = ApplicationBuilder().token(TOKEN).defaults(df).connection_pool_size(
        696).write_timeout(333).read_timeout(300).connect_timeout(333).build()

    commands = {
        "start": start_c,
        "help": help_c,
        "use": use_c,
        "ping": ping,
        "info": info_c,
        "surah": surah_c,
        "random": randomAyah,
        "rand": randomAyah,
        
    }

    callbacks = (
        surahCallback,

    )
    for i, j in commands.items():
        bot.add_handler(CommandHandler(i, j))

    for i in callbacks:
        bot.add_handler(CallbackQueryHandler(i))

    bot.add_handler(InlineQueryHandler(handleInlineQuery))

    bot.add_handler(MessageHandler(filters.TEXT, handleMessage))

    bot.run_polling()


if __name__ == "__main__":
    runBot()
