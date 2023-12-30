from ..quran import QuranClass

# Variables has to be declared before importing handlers
Quran = QuranClass()


from .helpers import generateSurahButtons

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

    allSurahInlineButtons = generateSurahButtons(
        Quran
        # generates a 2D list of buttons for all the surahs
        # Each page contains 33 buttons (11 rows of 3 buttons each)
        # Eg. [[[button1], [button2], [button3]], [[button4], [button5], [button6]], ...]
        # | 1  | 2  | 3  |
        # | 4  | 5  | 6  |
        # | 7  | 8  | 9  |
        # | 10 | 11 | 12 |
        # | 13 | 14 | 15 |
        # | 16 | 17 | 18 |
        # | 19 | 20 | 21 |
        # | 22 | 23 | 24 |
        # | 25 | 26 | 27 |
        # | 28 | 29 | 30 |
        # | 31 | 32 | 33 |
        # | Prev | Next |
    )


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
from .others import (
    pingCommand,
    infoCommand,
)

