from bot.quran import QuranClass

# Import after the class definition to avoid circular import
Quran = QuranClass()

from bot.handlers.helpers import generateSurahButtons


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


from .middleware import middleware
from .errorHandler import handleErrors
from .command import handlers as commandHandlers
from .message import handlers as messageHandlers
from .inlineQuery import handlers as inlineQueryHandlers
from .callbackQuery import handlers as callbackQueryHandlers
from .removeServiceMessages import handlers as removeChatMemberJoinMessages


exportedHandlers = [
    *commandHandlers,
    *messageHandlers,
    *inlineQueryHandlers,
    *callbackQueryHandlers,
    *removeChatMemberJoinMessages,
]
