import os
import asyncio

from telegram.ext import *
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, constants

from .handlers.database import db
from .handlers import exportedHandlers, handleErrors, middleware


# Load Environment Variables
load_dotenv()
LOCAL = os.environ.get("LOCAL")
TOKEN = os.environ.get("TOKEN") if not LOCAL else os.environ.get("TEST")


def runBot(token):
    df = Defaults(parse_mode=constants.ParseMode.HTML, block=False, quote=True)

    app = (
        ApplicationBuilder()
        .token(token)
        .defaults(df)
        .connection_pool_size(777)
        .write_timeout(333)
        .read_timeout(333)
        .connect_timeout(333)
        .build()
    )
    app.add_handler(
        TypeHandler(Update, middleware), group=-1
    )  # called in every update, then passed to other handlers

    app.add_handlers(handlers=exportedHandlers)

    app.add_error_handler(handleErrors)

    # Send a message to the admin when the bot starts
    loop = asyncio.get_event_loop()
    msg = f"<b>Bot started at {datetime.now().strftime('%d %B %Y, %H:%M:%S %A GMT+6')} 🚀</b>"
    loop.run_until_complete(app.bot.sendMessage(5596148289, msg))

    app.run_polling()


def startBot():
    if LOCAL:
        print("-" * 27)
        print("Running on local test Bot")
        print("-" * 27)

    if not TOKEN:
        print("Please put your bot token in `.env` file")
        print()
        return

    runBot(TOKEN)


if __name__ == "__main__":
    startBot()
