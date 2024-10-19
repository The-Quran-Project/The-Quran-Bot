import json, os

path = "bot/Data/audio/fileIDs.json"

with open(path, "rb") as file:
    _data = json.load(file)


def getSurahAudio(surah: int) -> str:
    return _data[str(surah)]

