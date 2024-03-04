from .. import Quran, replies
from ..database import db


def useTemplate(title, ayah, lang, restrictedLangs):
    if lang in restrictedLangs:
        return f"""
<u><b>{title}</b></u>
<blockquote>This group has restricted {title} translation. Admins can use /settings to change the preference.</blockquote>
"""

    return f"""
<u><b>{title}</b></u>
<blockquote>{ayah}</blockquote>
"""


def getAyahReplyFromPreference(surahNo, ayahNo, userID, restrictedLangs=None):
    """Returns the reply for the ayah"""
    if restrictedLangs == None:
        restrictedLangs = []

    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)

    user = db.getUser(userID)
    settings = user["settings"]
    primaryLanguage = settings["primary"]
    secondaryLanguage = settings["secondary"]
    otherLanguage = settings["other"]
    font = settings["font"]
    showTafsir = settings["showTafsir"]

    primary = Quran.detectLanguage(primaryLanguage)
    secondary = Quran.detectLanguage(secondaryLanguage)
    other = Quran.detectLanguage(otherLanguage)

    primaryTitle = Quran.getTitleLanguageFromAbbr(primaryLanguage)
    secondaryTitle = Quran.getTitleLanguageFromAbbr(secondaryLanguage)
    otherTitle = Quran.getTitleLanguageFromAbbr(otherLanguage)

    # If the user has a selected font ( only for Arabic ), then use the preferred font
    # it will be like "arabic_1" or "arabic_2"
    if primary == "arabic":
        primary = f"arabic_{font}"
    if secondary == "arabic":
        secondary = f"arabic_{font}"
    if other == "arabic":
        other = f"arabic_{font}"

    reply = f"""
Surah : <b>{surah} ({surahNo})</b>
Ayah  : <b>{ayahNo} out of {totalAyah}</b>
"""

    if primary:
        reply += useTemplate(
            primaryTitle, ayah[primary], primaryLanguage, restrictedLangs
        )
    if secondary:
        reply += useTemplate(
            secondaryTitle, ayah[secondary], secondaryLanguage, restrictedLangs
        )
    if other:
        reply += useTemplate(otherTitle, ayah[other], otherLanguage, restrictedLangs)

    if showTafsir:
        tafsir = ayah.tafsir
        reply += f"""
<b>Tafsir:</b> <a href="{tafsir}">Telegraph</a>
"""

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
    if language:
        lang = Quran.detectLanguage(language)

    languageTitle = Quran.getTitleLanguageFromAbbr(Quran.getAbbr(lang))
    ayah = Quran.getAyah(surahNo, ayahNo)[lang]
    reply = f"""
Surah : <b>{surah} ({surahNo})</b>
Ayah  : <b>{ayahNo} out of {totalAyah}</b>

<u><b>{languageTitle}</b></u>
<blockquote>{ayah}</blockquote>
"""

    return reply
