from telegram import Update, Bot, InlineKeyboardMarkup

from .helpers import getAyahReply, getAyahButton
from . import Constants
from . import Quran

from .callbackQueryHandlers import handleSettingsButtonPress


async def handleButtonPress(u: Update, c):
    """Handles all the button presses / callback queries"""
    message = u.effective_message
    userID = u.effective_user.id

    query = u.callback_query
    query_data = query.data
    group = u.effective_chat.id != userID

    async def edit_text(*a, **k):
        if "disable_web_page_preview" not in k:
            k["disable_web_page_preview"] = group
        await message.edit_text(*a, **k)

    if query_data.startswith("settings"):
        await handleSettingsButtonPress(u, c)

    elif query_data.startswith("audio"):
        surahNo, ayahNo = map(int, query_data.split()[1:])
        file_id = Quran.getAudioFile(surahNo, ayahNo)
        await message.reply_audio(file_id, quote=True)
        await query.answer()

    elif query_data.startswith("surah"):
        index = int(query_data.split()[1])

        surah = Quran.getSurahNameFromNumber(index)
        ans = f"You selected {surah}"

        await query.answer(ans)
        reply = getAyahReply(userID, index, 1)

        button = getAyahButton(index, 1)

        await edit_text(reply, reply_markup=button)

    elif query_data.startswith(("prev", "next")):
        index = int(query_data.split()[1])
        if query_data.split()[0] == "prev":
            index -= 1
        else:
            index += 1

        if index >= len(Constants.allSurahInlineButtons):
            index = 0

        button = InlineKeyboardMarkup(Constants.allSurahInlineButtons[index])

        await message.edit_reply_markup(button)

    elif query_data.startswith("goback"):
        surahNo, ayahNo = map(int, query_data.split()[1:])

        if surahNo == ayahNo == 1:
            surahNo = 114
            ayahNo = 6

        elif ayahNo == 1:
            surahNo -= 1
            ayahNo = Quran.getAyahNumberCount(surahNo)
        else:
            ayahNo -= 1

        reply = getAyahReply(userID, surahNo, ayahNo)

        button = getAyahButton(surahNo, ayahNo)

        await edit_text(reply, reply_markup=button)

    elif query_data.startswith("goforward"):
        surahNo, ayahNo = map(int, query_data.split()[1:])

        if surahNo == 114 and ayahNo == 6:
            surahNo = 1
            ayahNo = 1

        elif ayahNo >= Quran.getAyahNumberCount(surahNo):
            surahNo += 1
            ayahNo = 1
        else:
            ayahNo += 1

        reply = getAyahReply(userID, surahNo, ayahNo)

        button = getAyahButton(surahNo, ayahNo)

        await edit_text(reply, reply_markup=button)
