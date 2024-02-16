from .. import Quran, replies
from ..database import db


def getAyahReplyFromPreference(surahNo, ayahNo, userID):
    """Returns the reply for the ayah"""
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
        other = f"arabic{font}"

    reply = f"""
Surah : <b>{surah} ({surahNo})</b>
Ayah  : <b>{ayahNo} out of {totalAyah}</b>
"""
    template = """
<u><b>{title}</b></u>
<blockquote>{ayah}</blockquote>
"""
    if primary:
        reply += template.format(title=primaryTitle, ayah=ayah[primary])
    if secondary:
        reply += template.format(title=secondaryTitle, ayah=ayah[secondary])
    if other:
        reply += template.format(title=otherTitle, ayah=ayah[other])

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
