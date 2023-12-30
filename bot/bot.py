from telegram import constants
from telegram.ext import (
    filters,
    Defaults,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

import os

from .utils.keep_alive import runFlask
from .utils.log import startLogger
from .handlers import (
    startCommand,
    helpCommand,
    useCommand,
    surahCommand,
    randomCommand,
    handleButtonPress,
    handleInlineQuery,
    handleMessage,
    pingCommand,
    infoCommand,
)

load_dotenv()


# Environment Variables
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
        "rand": handleButtonPress,
    }

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

    startLogger(__name__)

    # run Flask server in production only
    if not LOCAL:
        runFlask()

    runBot(TOKEN)


if __name__ == "__main__":
    startBot()
