import secrets

from bot.handlers import Quran
from bot.handlers.helpers.getAyahButton import getAyahButton
from bot.handlers.helpers.getAyahReply import getAyahReplyFromPreference


def getRandomAyah(userID):
    """Returns a random ayah from the Quran"""
    randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
    ayahCount = Quran.getAyahNumberCount(randSurah)
    randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount`

    return {
        "reply": getAyahReplyFromPreference(randSurah, randAyah, userID),
        "buttons": getAyahButton(randSurah, randAyah, userID),
    }
