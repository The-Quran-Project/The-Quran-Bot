from telegram import Update, Bot

import secrets


from .. import Quran
from ..helpers import getAyahReply, getAyahButton


async def getRandomAyah():
    randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
    ayahCount = Quran.getAyahNumberCount(randSurah)
    randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount`

    return {
        "reply": getAyahReply(randSurah, randAyah),
        "button": getAyahButton(randSurah, randAyah),
    }
