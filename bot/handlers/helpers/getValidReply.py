from .. import Quran
from .getAyahButton import getAyahButton
from .getAyahReply import getAyahReply, getAyahReplyFromPreference


validFormat = """
Give like:

<pre>
surahNo : ayahNo
1:3
</pre>"""


def isValidFormat(text):
    sep = text.split(":")
    if text.isdecimal() and 1 <= int(text) <= 114:  # if only surah number is given
        return {
            "ok": "True",
            "message": None,
            "surahNo": int(text),
            "ayahNo": 1,
            "onlySurah": True,
        }

    if len(sep) != 2:
        return {
            "ok": False,
            "message": "<b>Your format is not correct.</b>" + validFormat,
        }

    surahNo, ayahNo = sep
    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdecimal() and ayahNo.isdecimal()):
        return {
            "ok": False,
            "message": "<b>Surah and Ayah number must be integers</b>" + validFormat,
        }

    surahNo = int(surahNo)

    if not 1 <= surahNo <= 114:
        return {
            "ok": False,
            "message": "<b>Surah number needs to be between <i>1</i> to <i>114</i>.</b>",
        }

    surahNo = int(surahNo)
    ayahNo = int(ayahNo)
    ayahCount = Quran.getAyahNumberCount(surahNo)

    if not 1 <= ayahNo <= ayahCount:
        return {
            "ok": False,
            "message": f"""
<b>Surah {Quran.getSurahNameFromNumber(surahNo)} has {ayahCount} ayahs only.</b>
You gave ayah no. {ayahNo}""",
        }

    return {
        "ok": True,
        "message": None,
        "surahNo": surahNo,
        "ayahNo": ayahNo,
    }


def getValidReply(userID, text, language=None, restrictedLangs: list = None):
    text = text.strip()

    x = isValidFormat(text)
    if x["ok"] == False:
        return {"text": x["message"], "buttons": None}

    surahNo = x["surahNo"]
    ayahNo = x["ayahNo"]
    if language:
        reply = getAyahReply(surahNo, ayahNo, language)
    else:
        reply = getAyahReplyFromPreference(
            surahNo, ayahNo, userID, restrictedLangs=restrictedLangs
        )
    buttons = getAyahButton(surahNo, ayahNo, userID, language)

    return {"text": reply, "buttons": buttons}
