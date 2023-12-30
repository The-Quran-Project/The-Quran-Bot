from .. import Quran
from . import getAyahReply, getAyahButton


async def getValidReply(userID, text: str):
    """Check the `text` and returns a valid reply"""
    sep = text.split(":")
    if len(sep) != 2:
        reply = """
<b>Your format is not correct.</b>
Give like:

<pre>
surahNo : ayahNo
1:3
</pre>
"""
        reply = {"text": reply, "button": None}
        return reply

    surahNo, ayahNo = sep
    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdecimal() and ayahNo.isdecimal()):
        reply = """
<b>Surah and Ayah number must be integers</b>
Give like:
<pre>
surahNo : ayahNo
1:3
</pre>
"""

        reply = {"text": reply, "button": None}
        return reply

    surahNo = int(surahNo)

    if not 1 <= surahNo <= 114:
        reply = """
<b>Surah number needs to be between <i>1</i> to <i>114</i>.</b>
"""

        reply = {"text": reply, "button": None}
        return reply

    surah = Quran.getSurahNameFromNumber(surahNo)
    ayahCount = Quran.getAyahNumberCount(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= ayahNo <= ayahCount:
        reply = f"""
<b>Surah {surah} has {ayahCount} ayahs only.</b>

But you gave ayah no. {ayahNo}
"""

        reply = {"text": reply, "button": None}
        return reply

    reply = getAyahReply(userID, surahNo, ayahNo)
    button = getAyahButton(surahNo, ayahNo)

    return {"text": reply, "button": button}
