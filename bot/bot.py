import os
# --- PIP Packages ---
from telegram import constants
from telegram.ext import (
    filters,
    Defaults,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv

# --- Local Packages ---
from .utils.keep_alive import runFlask
from .utils.log import startLogger
from .handlers import (
    start_c,
    help_c,
    use_c,
    ping,
    info_c,
    surah_c,
    randomAyah,
    surahCallback,
    handleInlineQuery,
    handleMessage
)

load_dotenv()


# Environment Variables
LOCAL = os.environ.get("LOCAL")
TOKEN = os.environ.get("TOKEN") if LOCAL else os.environ.get("TEST")


def runBot(token):
    df = Defaults(parse_mode=constants.ParseMode.HTML,
                  block=False, disable_web_page_preview=False)

    bot = ApplicationBuilder().token(token).defaults(df).connection_pool_size(
        777).write_timeout(333).read_timeout(333).connect_timeout(333).build()

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

    # Inline Keyboard.onclick Handler
    callbacks = (
        surahCallback,

    )

    for i, j in commands.items():
        bot.add_handler(CommandHandler(i, j))

    for i in callbacks:
        bot.add_handler(CallbackQueryHandler(i))

    # inline use handler. eg.
    #       @AlFurqanRobot 1:3
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

    # only running flask app if it is in production
    # It's using `threading`. So won't block other tasks
    if not LOCAL:
        runFlask()
    

    runBot(TOKEN)



if __name__ == "__main__":
    startBot()