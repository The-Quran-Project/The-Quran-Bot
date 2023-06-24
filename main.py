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

from handlers import *

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


def runFlask():
    app = flask.Flask("Quran Bot")

    @app.route('/')
    def index():
        return f"<h1>Running for {(time.time()-start)/60:.2f} minutes</h1>"

    app.run("0.0.0.0", 8080)


def main():
    df = Defaults(parse_mode=constants.ParseMode.HTML, block=False)

    bot = ApplicationBuilder().token(TOKEN).defaults(df).connection_pool_size(
        696).write_timeout(333).read_timeout(300).connect_timeout(333).build()

    commands = {
        "start": start_c,
        "help": help_c,
        "use": use_c,
        "ping": ping,
        "info": info_c,
        "surah": surah_c,

    }

    callbacks = (
        surahCallback,

    )
    for i, j in commands.items():
        bot.add_handler(CommandHandler(i, j))

    for i in callbacks:
        bot.add_handler(CallbackQueryHandler(i))

    bot.add_handler(MessageHandler(filters.TEXT, handleMessage))

    bot.run_polling()


if not IS_LOCAL:
    threading.Thread(target=runFlask).start()

if __name__ == "__main__":
    main()
