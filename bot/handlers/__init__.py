from ..quran import QuranClass

# Variables has to be declared before importing handlers
Quran = QuranClass()

from .helpers import generateSurahButtons
from .database import db as _


class Constants:
    # --- Stickers ---
    salamSticker = (
        "CAACAgUAAxkBAAIBEGOtH-MLc6D7antAIRlma1YgnMe7AAJnBAAC3uq4VANpwAelURpaLAQ"
    )

    inShaAllah = (
        "CAACAgUAAxkBAAIBEWOtH-OoB2EaecZw_DAqRwvbHlOZAALWAwACkni4VLa6DL4cB1H6LAQ"
    )
    jazakAllah = (
        "CAACAgUAAxkBAAIBEmOtH-No3_xEGMh2YpM6ErBQ2BHHAAK4AwAC8Yq5VFbQH8fyZNceLAQ"
    )
    allSurahInlineButtons = generateSurahButtons(Quran)
    languages = ("ar", "en")


# --- Importing Handlers ---
from .commands import (
    startCommand,
    helpCommand,
    aboutCommand,
    useCommand,
    surahCommand,
    getCommand,
    getWithLanguage,
    audioCommand,
    tafsirCommand,
    randomCommand,
)
from .others import (
    pingCommand,
    infoCommand,
)
from .handleMessage import handleMessage
from .handleButtonPress import handleButtonPress
from .handleInlineQuery import handleInlineQuery
from .helpers.updateSettings import updateSettings
from .middleware import middleware
from .adminCommand import adminCommand
