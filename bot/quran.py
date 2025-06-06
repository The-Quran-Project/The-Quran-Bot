import os
import json
import secrets

from bot.utils.searchSurah import fuzzySearchSurah


"""
Structure of json files in Data folder:
	english:
		[ [ayah1, ayah2, ...], [ayah1, ayah2, ...] ]


	arabic:
		[ [[ayah1-uthmani, ayah1-simple], [ayah2, ayah2], ...] ]


	surahNames:
		["Al-Fatihah", "Al-Baqarah", "Ali 'Imran", ...]

"""


class objectify:
    english_1: str
    english_2: str
    arabic: str
    arabic_1: str
    arabic_2: str
    bengali: str
    urdu: str
    hindi: str
    german: str
    kurdish: str
    persian: str
    russian: str
    uzbek: str
    tafsir: str

    def __init__(self, entries):
        self.__dict__.update(entries)

    def __getitem__(self, key):
        return self.__dict__[key]


# Get the absolute path of the directory that contains this file
DIR_PATH = (
    os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/Data"
)  # root/Data


class QuranClass:
    languages = "arabic english_1 english_2 bengali urdu hindi german kurdish persian russian uzbek".split()
    abbreviations = {
        "arabic": "ar",
        "english_1": "en",
        "english_2": "en2",
        "bengali": "be",
        "urdu": "ur",
        "hindi": "hi",
        "german": "ge",
        "kurdish": "ku",
        "persian": "pe",
        "russian": "ru",
        "uzbek": "uz",
    }

    titleLanguages = {
        "ar": "Arabic",
        "en": "English",
        "en2": "English (Mufti Taqi Usmani)",
        "be": "Bengali",
        "ur": "Urdu",
        "hi": "Hindi",
        "ge": "German",
        "ku": "Kurdish",
        "pe": "Persian",
        "ru": "Russian",
        "uz": "Uzbek",
    }

    DATA = {}
    for lang in languages:
        with open(f"{DIR_PATH}/quran_{lang}.json", "rb") as f:
            DATA[lang] = json.load(f)

    with open(f"{DIR_PATH}/tafsirs.json", "rb") as f:
        TAFSIRS = json.load(f)

    with open(f"{DIR_PATH}/surahNames.json", "rb") as f:
        SURAH_NAMES = json.load(f)

    def __init__(self):
        pass

    def getAyah(self, surahNo: int, ayahNo: int) -> objectify:
        """
        Returns Arabic, English and Tafsir of the specified ayah.


        Args:
            - `self`: the object instance of a Quran class.
            - `surahNo` (int): the number or name of the surah to retrieve the ayah from.
            - `ayahNo` (int): the number of the ayah to retrieve.

        Returns:
            - An objectify object that contains the following three keys:
            - `english_1`: The English translation of the ayah.
            - `english_2`: The English translation of the ayah by Mufti Taqi Usmani.
            - `arabic_1` : The Arabic text of the ayah in the Uthmani script.
            - `arabic_2` : The Arabic text of the ayah in the Simple script.
            - `bengali`  : The Bengali translation of the ayah.
            - `urdu`     : The Urdu translation of the ayah.
            - `hindi`    : The Hindi translation of the ayah.
            - `german`   : The German translation
            - `kurdish`  : The Kurdish translation
            - `persian`  : The Persian translation
            - `russian`  : The Russian translation
            - `uzbek`   : The Uzbek translation
            - `tafsir`   : The telegra.ph link of the tafsir of that verse.
        """

        surahNo = int(surahNo)
        ayahNo = int(ayahNo)
        surahNo = int(surahNo)
        result = {}

        for lang in self.languages:
            result[lang] = self.DATA[lang][surahNo - 1][ayahNo - 1]

        z = result["arabic"]

        del result["arabic"]
        graph = f"https://telegra.ph/{self.TAFSIRS[f'{surahNo}_{ayahNo}']}"

        res = {
            "arabic_1": z[0],
            "arabic": z[0],
            "arabic_2": z[1],
            **result,
            "tafsir": graph,
        }

        return objectify(res)

    def random(self):
        randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
        ayahCount = self.getAyahNumberCount(randSurah)
        randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount`

        return {
            "verse": self.getAyah(randSurah, randAyah),
            "surahNo": randSurah,
            "ayahNo": randAyah,
            "totalAyah": ayahCount,
        }

    def getSurahNames(self):
        return self.SURAH_NAMES

    def getSurahNameFromNumber(self, surahNumber: int):
        surahNumber = int(surahNumber) - 1
        name = self.SURAH_NAMES[surahNumber]
        return name

    def getAyahNumberCount(self, surahNo: int):
        surahNo = int(surahNo)
        return len(self.DATA["english_2"][surahNo - 1])

    def searchSurah(self, string):
        return fuzzySearchSurah(string)

    def detectLanguage(self, text: str):
        if not text:
            return None

        text = text.lower()
        if text == "en2":
            return "english_2"  # Mufti Taqi Usmani
        if text == "english2":
            return "english_2"
        if text == "bn":
            return "bengali"

        # print(f"Detecting language for: {text}")
        # print(f"Available languages: {self.languages}")

        for lang in self.languages:
            if lang.startswith(text):
                return lang
        return None

    def getAbbr(self, lang):
        if not lang:
            return "None"

        return self.abbreviations[lang]

    def getTitleLanguageFromAbbr(self, abbr):
        if not abbr or abbr == "None":
            return None

        return self.titleLanguages[abbr]

    def getTitleLanguageFromLang(self, lang):
        if not lang or lang == "None":
            return None

        return self.titleLanguages[self.getAbbr(lang)]

    def getLanguages(self) -> dict:
        return self.titleLanguages.items()


if __name__ == "__main__":
    q = QuranClass()
    print(q.getLanguages())
