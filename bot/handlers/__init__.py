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


# --- Importing Handlers ---
from .commands import (
    startCommand,
    helpCommand,
    useCommand,
    surahCommand,
    surahCommand,
    randomCommand,
)
from .handleMessage import handleMessage
from .handleButtonPress import handleButtonPress
from .handleButtonPress import handleButtonPress
from .handleInlineQuery import handleInlineQuery
from .helpers.updateSettings import updateSettings
from .middleware import middleware
from .others import (
    pingCommand,
    infoCommand,
)
