from telegram import Update, constants
from telegram.ext import *
from dotenv import load_dotenv

import os

from .handlers import *


# Load Environment Variables
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
        "about": aboutCommand,
        "use": useCommand,
        "ping": pingCommand,
        "info": infoCommand,
        "surah": surahCommand,
        "get": getCommand,
        "audio": audioCommand,
        "tafsir": tafsirCommand,
        "random": randomCommand,
        "rand": randomCommand,
        "settings": updateSettings,
    }

    bot.add_handler(
        TypeHandler(Update, middleware), group=-1
    )  # called in every update, then passed to other handlers

    for cmd, handler in commands.items():
        bot.add_handler(CommandHandler(cmd, handler))

    bot.add_handler(CommandHandler("admin", adminCommand, filters.ChatType.PRIVATE))

    bot.add_handler(CallbackQueryHandler(handleButtonPress))
    bot.add_handler(InlineQueryHandler(handleInlineQuery))
    bot.add_handler(MessageHandler(filters.Regex(r"/get[a-zA-Z]{2}"), getWithLanguage))
    bot.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handleMessage)
    )  # for private chats
    bot.add_error_handler(handleErrors)

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
