import os
import asyncio
import time

from telegram.ext import *
from dotenv import load_dotenv
from telegram import Update, constants
from datetime import datetime, timezone

from bot.handlers.sendScheduled import jobSendScheduled
from bot.handlers import exportedHandlers, handleErrors, middleware
from bot.utils import getArguments

# Load Environment Variables
load_dotenv()


LOCAL = os.environ.get("LOCAL") or getArguments().ARG_LOCAL
TOKEN = os.environ.get("TOKEN") if not LOCAL else os.environ.get("TEST")
TOKEN = "6643208326:AAGoUhxF3JjaRolbMMSf6qLtMnEPP6s4rKA"

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

    if not LOCAL:
        app.job_queue.run_repeating(jobSendScheduled, 60, name="scheduledMessages")

    app.add_handler(
        TypeHandler(Update, middleware), group=-19
    )  # called in every update, then passed to other handlers

    app.add_handlers(handlers=exportedHandlers)

    app.add_error_handler(handleErrors)

    # Send a message to the admin when the bot starts
    loop = asyncio.get_event_loop()

    msg = f"<b>Bot started at {datetime.now(timezone.utc).strftime('%d %B %Y, %H:%M:%S %A UTC')} 🚀</b>"
    print(msg[3:-4])
    loop.run_until_complete(app.bot.sendMessage(5596148289, msg))

    app.run_polling()


def startBot():
    if not TOKEN:
        print("Please put your bot token in `.env` file")
        exit()
        return

    if LOCAL:
        print("-" * 27)
        print("Running on local test Bot")
        print("-" * 27)

    runBot(TOKEN)


if __name__ == "__main__":
    startBot()
