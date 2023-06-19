import httpx
import json
import time
import os
from debugger import Debug


def Prettify(a):
    return json.dumps(a, ensure_ascii=0, indent=3)


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def writeAyah(surah, ayah, text):
    file_path = f"Data/{surah}/text/{ayah}.txt"
    with open(file_path, 'w', encoding="utf8") as f:
        f.write(text)


def writeAudio(surah, ayah, url):
    file_path = f"Data/{surah}/audio/{ayah}.mp3"
    audio = ses.get(url, follow_redirects=1).content
    with open(file_path, 'wb') as f:
        f.write(audio)


url = "https://api.alquran.cloud/v1/surah/{}/ar.alafasy"

ses = httpx.Client(timeout=None)

for i in range(1, 115):
    r = httpx.get(url.format(i)).json().get("data")

    englishName = r.get("englishName")
    englishNameTranslation = r.get("englishNameTranslation")
    numberOfAyahs = r.get("numberOfAyahs")
    arabicName = r.get("name")
    create_folder(f"Data/{i}/text")
    create_folder(f"Data/{i}/audio")

    data = {
        "name": englishName,
        "meaning": englishNameTranslation,
        "arabicName": arabicName,
        "numberOfAyahs": numberOfAyahs
    }

    # Dumping json data of the Surah
    with open(f"Data/{i}/data.json", 'w') as f:
        json.dump(data, f, ensure_ascii=0, indent=3)

    AYAHS = r.get("ayahs")[1:]

    for j, surah in enumerate(AYAHS, start=1):
        text = surah.get("text")
        writeAyah(i, j, text)
        audio = surah.get("audio")
        writeAudio(i, j, audio)

        print("Done", i, j)

    print()
    print("Completed", i, englishName)
    print()
    break
