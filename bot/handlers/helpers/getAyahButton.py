from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def getAyahButton(surahNo: int or str, ayahNo: int or str, arabicStyle: int = 2):
    """Returns the button for the ayah"""
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Prev", callback_data=f"goback {surahNo} {ayahNo}"
                ),
                InlineKeyboardButton(
                    "Next", callback_data=f"goforward  {surahNo} {ayahNo}"
                ),
            ],
            [
                # InlineKeyboardButton(
                #     "Change Arabic Style",
                #     callback_data=f"change-arabic  {surahNo} {ayahNo} {arabicStyle}",
                # ),
                InlineKeyboardButton(
                    "Audio", callback_data=f"audio {surahNo} {ayahNo}"
                ),
            ],
        ]
    )

    return button
