import json
from bot.handlers.database import db


path = "bot/Data/audio/fileIDs.json"

with open(path, "rb") as file:
    _data = json.load(file)


def getSurahAudio(surah: int, userID: int) -> str:
    preferredReciter = str(db.getUser(userID)["settings"]["reciter"])
    return _data[preferredReciter][int(surah) - 1]
