from .. import Quran
from . import getAyahReply, getAyahButton


validFormat = """
Give like:

<pre>
surahNo : ayahNo
1:3
</pre>"""


def getValidReply(
    userID: int, text: str, language: str = None
) -> dict[str, str | None]:
    """Check the `text` and returns a valid reply"""

    if (
        text.strip().isdigit() and 1 <= int(text.strip()) <= 114
    ):  # if only surah number is given
        surahNo = int(text.strip())
        ayahNo = 1
        surah = Quran.getSurahNameFromNumber(surahNo)
        ayahCount = Quran.getAyahNumberCount(surahNo)
        reply = getAyahReply(userID, surahNo, ayahNo, language)
        button = getAyahButton(surahNo, ayahNo, userID)

        return {"text": reply, "button": button}

    sep = text.split(":")
    if len(sep) != 2:
        reply = "<b>Your format is not correct.</b>" + validFormat
        reply = {"text": reply, "button": None}
        return reply

    surahNo, ayahNo = sep
    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdecimal() and ayahNo.isdecimal()):
        reply = "<b>Surah and Ayah number must be integers</b>" + validFormat

        return {"text": reply, "button": None}

    surahNo = int(surahNo)

    if not 1 <= surahNo <= 114:
        reply = "<b>Surah number needs to be between <i>1</i> to <i>114</i>.</b>"
        return {"text": reply, "button": None}

    surah = Quran.getSurahNameFromNumber(surahNo)
    ayahCount = Quran.getAyahNumberCount(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= ayahNo <= ayahCount:
        reply = f"""
<b>Surah {surah} has {ayahCount} ayahs only.</b>

But you gave ayah no. {ayahNo}
"""

        return {"text": reply, "button": None}

    reply = getAyahReply(userID, surahNo, ayahNo, language)
    button = getAyahButton(surahNo, ayahNo, userID)

    return {"text": reply, "button": button}
