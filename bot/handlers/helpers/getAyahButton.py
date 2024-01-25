from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def getAyahButton(surahNo: int, ayahNo: int, userID: int):
    """Returns the button for the ayah"""
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Prev", callback_data=f"goback {surahNo} {ayahNo} {userID}"
                ),
                InlineKeyboardButton(
                    "Next", callback_data=f"goforward  {surahNo} {ayahNo} {userID}"
                ),
            ],
            [
                # InlineKeyboardButton(
                #     "Change Arabic Style",
                #     callback_data=f"change-arabic  {surahNo} {ayahNo} {arabicStyle}",
                # ),
                InlineKeyboardButton(
                    "Audio", callback_data=f"audio {surahNo} {ayahNo} {userID}"
                ),
                InlineKeyboardButton(
                    "Open in Quran.com",
                    url=f"https://quran.com/{surahNo}:{ayahNo}",
                ),
            ],
        ]
    )

    return button
