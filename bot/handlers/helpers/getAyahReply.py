from .. import Quran, replies

def getAyahReply(surahNo: int or str, ayahNo: int or str, arabicStyle: int = 1):
    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)
    arabic = ayah.arabic if arabicStyle == 1 else ayah.arabic2

    reply = replies.sendAyahFull.format(
        surahName=surah,
        surahNo=surahNo,
        ayahNo=ayahNo,
        totalAyah=totalAyah,
        arabic=arabic,
        english=ayah.english,
        tafsir=ayah.tafsir,
    )

    return reply
