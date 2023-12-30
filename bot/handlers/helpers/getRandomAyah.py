from telegram import Update, Bot

import secrets


from .. import Quran
from ..helpers import getAyahReply, getAyahButton


def getRandomAyah(userID):
    randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
    ayahCount = Quran.getAyahNumberCount(randSurah)
    randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount`

    return {
        "reply": getAyahReply(userID, randSurah, randAyah),
        "button": getAyahButton(randSurah, randAyah),
    }
