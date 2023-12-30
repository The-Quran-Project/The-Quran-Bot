from telegram import Update, Bot, InlineKeyboardMarkup

from .helpers import getAyahReply, getAyahButton
from . import Constants
from . import Quran

from .callbackQueryHandlers import handleSettingsButtonPress


async def handleButtonPress(u: Update, c):
    """Handles all the button presses / callback queries"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id

    query = u.callback_query
    query_data = query.data
    group = u.effective_chat.id != userID

    async def edit_text(*a, **k):
        if "disable_web_page_preview" not in k:
            k["disable_web_page_preview"] = group
        await message.edit_text(*a, **k)

    # print("Callback Data:", query_data)

    if query_data.startswith("surah"):
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

    # Toggling the style of Arabic.
    # Toggle between Uthmani and Simple
    elif query_data.startswith("change-arabic"):
        surahNo, ayahNo, arabicStyle = map(int, query_data.split()[1:])

        surah = Quran.getSurahNameFromNumber(surahNo)
        toggle = {1: 2, 2: 1}
        reply = getAyahReply(userID, surahNo, ayahNo)
        await edit_text(
            reply, reply_markup=getAyahButton(surahNo, ayahNo, toggle[arabicStyle])
        )

    elif query_data.startswith("settings"):
        await handleSettingsButtonPress(u, c)

    elif query_data.startswith("audio"):
        surahNo, ayahNo = map(int, query_data.split()[1:])
        file_id = Quran.getAudioFile(surahNo, ayahNo)
        await bot.sendAudio(chatID, file_id, reply_to_message_id=message.message_id)
        await query.answer()
