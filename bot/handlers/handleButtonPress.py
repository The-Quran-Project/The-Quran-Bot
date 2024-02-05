from telegram import Update, InlineKeyboardMarkup

from .helpers import getAyahReply, getAyahButton
from . import Constants
from . import Quran
from .database import db

from .callbackQueryHandlers import handleSettingsButtonPress, handleAdminButtonPress


async def handleButtonPress(u: Update, c):
    """Handles all the button presses / callback queries"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id

    query = u.callback_query
    queryData = query.data
    isGroup = chatID != userID

    async def edit_text(*a, **k):
        await message.edit_text(*a, **k)

    messageOwnerID = queryData.split()[-1]

    if (
        len(messageOwnerID) >= 9  # naive way to check if it's a valid id
        and isGroup
        and str(userID) != messageOwnerID
        and queryData.split()[0] not in "surahName prev next".split()
    ):
        await query.answer("Only the message owner can use this button")
        return

    if queryData.startswith("settings"):
        await handleSettingsButtonPress(u, c)

    elif queryData.startswith("admin"):
        await handleAdminButtonPress(u, c)

    elif queryData.startswith("audio"):
        surahNo, ayahNo = map(int, queryData.split()[1:-1])
        # file_id = Quran.getAudioFile(surahNo, ayahNo)
        # await message.reply_audio(file_id)
        await message.reply_audio(
            f"""https://quranaudio.pages.dev/{db.getUser(userID)["settings"]["reciter"]}/{
                surahNo}_{ayahNo}.mp3""",
            quote=True,
        )
        await query.answer()

    elif queryData.startswith("surah"):
        index = int(queryData.split()[1])

        surah = Quran.getSurahNameFromNumber(index)
        ans = f"You selected {surah}"

        await query.answer(ans)
        reply = getAyahReply(userID, index, 1)

        button = getAyahButton(index, 1, userID)

        await edit_text(reply, reply_markup=button)

    elif queryData.startswith(("prev", "next")):
        # Going between Surah Name Pages
        index = int(queryData.split()[1])
        if queryData.split()[0] == "prev":
            index -= 1
        else:
            index += 1

        if index >= len(Constants.allSurahInlineButtons):
            index = 0

        button = InlineKeyboardMarkup(Constants.allSurahInlineButtons[index])

        await message.edit_reply_markup(button)

    elif queryData.startswith("goback"):
        # Previous Ayah
        try:
            surahNo, ayahNo = map(int, queryData.split()[1:-1])
        except ValueError:
            surahNo, ayahNo = map(int, queryData.split()[1:])
        if surahNo == ayahNo == 1:
            surahNo = 114
            ayahNo = 6

        elif ayahNo == 1:
            surahNo -= 1
            ayahNo = Quran.getAyahNumberCount(surahNo)
        else:
            ayahNo -= 1

        reply = getAyahReply(userID, surahNo, ayahNo)

        button = getAyahButton(surahNo, ayahNo, userID)

        await edit_text(reply, reply_markup=button)

    elif queryData.startswith("goforward"):
        # Next Ayah
        try:
            surahNo, ayahNo = map(int, queryData.split()[1:-1])
        except ValueError:
            surahNo, ayahNo = map(int, queryData.split()[1:])

        if surahNo == 114 and ayahNo == 6:
            surahNo = 1
            ayahNo = 1

        elif ayahNo >= Quran.getAyahNumberCount(surahNo):
            surahNo += 1
            ayahNo = 1
        else:
            ayahNo += 1

        reply = getAyahReply(userID, surahNo, ayahNo)

        button = getAyahButton(surahNo, ayahNo, userID)

        await edit_text(reply, reply_markup=button)
