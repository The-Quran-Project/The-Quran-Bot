import os
import asyncio

from telegram.ext import *
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, constants

from .handlers import *
from .handlers.database import db


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
        ("random", "rand"): randomCommand,
        (
            "translations",
            "langs",
            "languages",
        ): translationsCommand,  # "languages" is an alias for "translations"
        "settings": updateSettings,
    }
    adminCommands = {
        "admin": adminCommand,
        "forward": forwardMessage,
        "getUser": getUser,
        "eval": evaluateCode,
    }

    for cmd, handler in commands.items():
        if type(cmd) == list:
            for alias in cmd:
                app.add_handler(
                    CommandHandler(alias, handler, ~filters.ChatType.CHANNEL)
                )
            continue

        app.add_handler(CommandHandler(cmd, handler, ~filters.ChatType.CHANNEL))

    for cmd, handler in adminCommands.items():
        app.add_handler(CommandHandler(cmd, handler, filters.User(db.getAllAdmins())))

    app.add_handler(CallbackQueryHandler(handleButtonPress))
    app.add_handler(InlineQueryHandler(handleInlineQuery))
    app.add_handler(
        MessageHandler(
            (~filters.ChatType.CHANNEL)
            & filters.Regex(
                r"^\/([A-Za-z]{1,10})\s\d+\s?:*\s?\d*$"
            ),  # match: /<lang> <surah>:<ayah> or /<lang> <surah>
            getTranslationCommand,
        )
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.ChatType.CHANNEL, handleMessage)
    )

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
