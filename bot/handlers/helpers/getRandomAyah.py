import secrets

from .. import Quran
from .getAyahButton import getAyahButton
from .getAyahReply import getAyahReplyFromPreference


def getRandomAyah(userID):
    """Returns a random ayah from the Quran"""
    randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
    ayahCount = Quran.getAyahNumberCount(randSurah)
    randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount`

    return {
        "reply": getAyahReplyFromPreference(randSurah, randAyah, userID),
        "buttons": getAyahButton(randSurah, randAyah, userID),
    }
