import json

surahFileIDPath = "bot/Data/audio/fileIDs.json"
VERSE_AUDIO_URL = (
    "https://the-quran-project.github.io/Quran-Audio/Data/{reciter}/{surah}_{ayah}.mp3"
)
CHAPTER_AUDIO_URL = "https://github.com/The-Quran-Project/Quran-Audio-Chapters/raw/refs/heads/main/Data/{reciter}/{surah}.mp3"

with open(surahFileIDPath, "r", encoding="utf-8") as f:
    surahIDs = json.load(f)


def getSurahFileID(surahNo: int, reciter: str) -> str | None:
    """Get the file ID of a Surah for a specific reciter from the JSON file."""

    reciterData = surahIDs.get(str(reciter))
    if not reciterData:
        return None

    return reciterData[int(surahNo) - 1]


def getAudioUrlOrID(
    surah: int, ayah: int, reciter: int = None, forceUrl=False, onlySurah=False
) -> str:
    if reciter is None:
        reciter = 1
    
    if onlySurah and not forceUrl:
        return getSurahFileID(surah, str(reciter))
    elif onlySurah and forceUrl:
        return CHAPTER_AUDIO_URL.format(reciter=reciter, surah=surah)

    return VERSE_AUDIO_URL.format(reciter=reciter, surah=surah, ayah=ayah)
