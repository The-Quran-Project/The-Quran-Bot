from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def getAyahButton(surahNo: int, ayahNo: int, userID: int, language: str = None):
    """Returns the buttons for the ayah"""

    # Get the first 3 letters of the language code
    # so when the user clicks on the buttons,
    # the bot can decide in which language to send the ayah.
    abbr = language[:3] if language else ""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Previous",
                    callback_data=f"prev_ayah {surahNo} {ayahNo} {abbr} {userID}",
                ),
                InlineKeyboardButton(
                    "Next",
                    callback_data=f"next_ayah {surahNo} {ayahNo} {abbr} {userID}",
                ),
            ],
            [
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

    return buttons
