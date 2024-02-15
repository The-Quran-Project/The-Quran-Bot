from .. import Quran, replies
from ..database import db


def getAyahReplyFromPreference(userID, surahNo, ayahNo, language=None):
    """Returns the reply for the ayah"""
    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)

    user = db.getUser(userID)
    settings = user["settings"]
    primaryLanguage = settings["primary"]
    secondaryLanguage = settings["secondary"]
    otherLanguage = settings["other"]
    arabicStyle = settings["arabicStyle"]
    showTafsir = settings["showTafsir"]

    arabic = f"""
<u><b>Arabic</b></u>
{ayah.arabic1 if arabicStyle == 1 else ayah.arabic2}
"""

    english = f"""
<u><b>English</b></u>
{ayah.english}
"""

    tafsir = f"""
<u><b>Tafsir</b></u>
<b>Read Here: <a href="{ayah.tafsir}">Telegraph</a></b>
"""

    reply = replies.sendAyah.format(
        surahName=surah,
        surahNo=surahNo,
        ayahNo=ayahNo,
        totalAyah=totalAyah,
    )

    return "Hello From Preference"

    if language:
        reply += {
            "en": english,
            "ar": arabic,
        }[language]

    elif ayahMode == 1:
        reply += arabic + english
    elif ayahMode == 2:
        reply += arabic
    elif ayahMode == 3:
        reply += english

    if showTafsir:
        reply += tafsir

    return reply


def getAyahReply(surahNo, ayahNo, language):
    """Returns the reply for the ayah"""
    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)

    reply = replies.sendAyah.format(
        surahName=surah,
        surahNo=surahNo,
        ayahNo=ayahNo,
        totalAyah=totalAyah,
    )
    ayah = Quran.getAyah(surahNo, ayahNo)
    print(ayah)
    return "Hello From getAyahReply"