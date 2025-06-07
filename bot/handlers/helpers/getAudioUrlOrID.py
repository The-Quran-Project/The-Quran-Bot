import json


VERSE_AUDIO_URL = (
    "https://the-quran-project.github.io/Quran-Audio/Data/{reciter}/{surah}_{ayah}.mp3"
)
CHAPTER_AUDIO_URL = "https://github.com/The-Quran-Project/Quran-Audio-Chapters/raw/refs/heads/main/Data/{reciter}/{surah}.mp3"


with open("bot/Data/audio/fileIDs.json", "rb") as f:
    fileIDs = json.load(f)


def getAudioUrlOrID(reciter: int, surah: int, ayah: int, forceUrl=False) -> str:
    if reciter is None:
        reciter = 1

    if ayah:  # If ayah is specified, return the URL
        return VERSE_AUDIO_URL.format(reciter=reciter, surah=surah, ayah=ayah)

    if forceUrl:  # If forceUrl is True, return the URL for chapter audio
        return CHAPTER_AUDIO_URL.format(reciter=reciter, surah=surah)

    # return the ID for surah recitation
    return fileIDs[str(reciter)][int(surah) - 1]
