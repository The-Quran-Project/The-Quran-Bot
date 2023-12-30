# pylint:disable=W0105
import os
import json
from .utils import AyahNumberInvalid, SurahNumberInvalid


"""
Structure of json files in Data folder:
	quran_en:
		{
		  "1":[ayah1, ayah2, ...],		  	"2":[ayah1, ...]
			}


	quran_ar:
		{
		  "1":[[ayah1-with-harakat, ayah1-without-harakat], [ayah2, ayah2], ...]
			}


	surah:
		["Al-Fatihah", "Al-Baqarah", "Ali 'Imran", ...]



"""


class objectify:
    def __init__(self, entries):
        self.english: str = ""
        self.arabic: str = ""
        self.arabic2: str = ""
        self.tafsir: str = ""
        self.__dict__.update(entries)


# Get the absolute path of the directory that contains this file
DIR_PATH = (
    os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/Data"
)  # root/Data


class QuranClass:
    with open(f"{DIR_PATH}/quran_en.json", "rb") as _f, open(
        f"{DIR_PATH}/quran_ar.json", "rb"
    ) as _g, open(f"{DIR_PATH}/surah.json", "rb") as _h, open(
        f"{DIR_PATH}/audio_file_ids.json", "rb"
    ) as _i, open(
        f"{DIR_PATH}/tafsirs.json", "rb"
    ) as _j:
        _AYAHS_en = json.load(_f)
        _AYAHS_ar = json.load(_g)
        SURAHS = json.load(_h)
        _FILE_ids = json.load(_i)
        _TAFSIRS = json.load(_j)

    def __init__(self):
        pass

    def getAyah(self, surahNo: int or str, ayahNo: int or str) -> objectify:
        """Returns English and two versions of Arabic text


        Args:
            - `self`: the object instance of a Quran class.
            - `surahNo` (int or str): the number or name of the surah to retrieve the ayah from.
            - `ayahNo` (int or str): the number of the ayah to retrieve.

        Returns:
            - An objectify object that contains the following three keys:
            - `english`: the English translation of the ayah.
            - `arabic`: the Arabic text of the ayah in the Uthmani script.
            - `arabic_2`: the Arabic text of the ayah in the Simple script.
            - `tafsir`: The telegra.ph link of the tafsir of that verse.

        Raises:
            - `SurahNumberInvalid`: if the `surahNo` is not a valid surah number (i.e. not between 1 and 114).
            - `AyahNumberInvalid`: if the `ayahNo` is greater than the number of ayahs in the specified surah.

        """

        surahNo = int(surahNo)
        ayahNo = int(ayahNo)

        if surahNo <= 0 or surahNo > 114:
            raise SurahNumberInvalid(
                f"Surah Number must be in between 1 to 114. `{surahNo}` is invalid."
            )

        surahNo = str(surahNo)
        x = self._AYAHS_en[surahNo]
        y = len(x)

        if ayahNo > y:
            raise AyahNumberInvalid(f"Surah {surahNo} has `{y}` ayahs only.")

        z = self._AYAHS_ar[surahNo][ayahNo - 1]

        graph = f"https://telegra.ph/{self._TAFSIRS[f'{surahNo}_{ayahNo}']}"

        res = {
            "english": x[ayahNo - 1],
            "arabic": z[0],
            "arabic2": z[1],
            "tafsir": graph,
        }

        return objectify(res)

    def getSurahNameFromNumber(self, ayahNumber: str or int):
        ayahNumber = int(ayahNumber) - 1

        name = self.SURAHS[ayahNumber]

        return name

    def getAyahNumberCount(self, surahNo: int or str):
        surahNo = int(surahNo)

        if not 1 <= surahNo <= 114:
            return 0

        return len(self._AYAHS_en[str(surahNo)])

    def getAudioFile(self, surahNo: int or str, ayahNo: int or str):
        return self._FILE_ids.get(f"{surahNo}_{ayahNo}")

    def searchSurah(self, string):
        matching_strings = []
        exact_match = False
        string_list = sorted(self.SURAHS)

        for s in string_list:
            a = s.split("-")[-1].lower()
            b = string.lower()
            c = b.replace("k", "q")
            if b == a:
                exact_match = True
                matching_strings = [s]
                break
            elif a.replace("'", "").strip() in string.lower():
                matching_strings.append(s)
            elif c == a:
                matching_strings.append(s)

        if not exact_match:
            for s in string_list:
                s_lower = s.split("-")[-1].lower()
                string_lower = string.lower()
                if all(c in s_lower for c in string_lower):
                    matching_strings.append(s)
                elif all(c in string_lower for c in s_lower):
                    matching_strings.append(s)
        matching_strings = list({i: 0 for i in matching_strings})[:3]

        data = [[surah, self.SURAHS.index(surah) + 1] for surah in matching_strings]
        data.sort(key=lambda x: x[1])

        return data
