from bot.handlers import Quran


def getNextAyah(surahNo: int, ayahNo: int):
    if surahNo == 114 and ayahNo == 6:
        return 1, 1
    if ayahNo >= Quran.getAyahNumberCount(surahNo):
        return surahNo + 1, 1
    return surahNo, ayahNo + 1


def getPrevAyah(surahNo: int, ayahNo: int):
    if surahNo == 1 and ayahNo == 1:
        return 114, 6
    if ayahNo == 1:
        prev_surah = surahNo - 1
        return prev_surah, Quran.getAyahNumberCount(prev_surah)
    return surahNo, ayahNo - 1
