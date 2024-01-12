from telegram import Update, constants
from telegram.ext import *
from dotenv import load_dotenv

import os

from .handlers import *



# Environment Variables
load_dotenv()
LOCAL = os.environ.get("LOCAL")
TOKEN = os.environ.get("TOKEN") if not LOCAL else os.environ.get("TEST")


def runBot(token):
    df = Defaults(
        parse_mode=constants.ParseMode.HTML, block=False, disable_web_page_preview=False
    )

    bot = (
        ApplicationBuilder()
        .token(token)
        .defaults(df)
        .connection_pool_size(777)
        .write_timeout(333)
        .read_timeout(333)
        .connect_timeout(333)
        .build()
    )

    commands = {
        "start": startCommand,
        "help": helpCommand,
        "use": useCommand,
        "ping": pingCommand,
        "info": infoCommand,
        "surah": surahCommand,
        "random": randomCommand,
        "rand": randomCommand,
        "settings": updateSettings,
    }

    bot.add_handler(
        TypeHandler(Update, middleware), group=-1
    )  # called in every update, then passed to other handlers

    for i, j in commands.items():
        bot.add_handler(CommandHandler(i, j))

    bot.add_handler(CallbackQueryHandler(handleButtonPress))
    bot.add_handler(InlineQueryHandler(handleInlineQuery))
    bot.add_handler(MessageHandler(filters.TEXT, handleMessage))

    bot.run_polling()


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
