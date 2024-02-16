from telegram import Update, InlineKeyboardMarkup

from .helpers import getAyahReply, getAyahReplyFromPreference, getAyahButton
from . import Constants
from . import Quran
from .database import db

from .callbackQueryHandlers import handleSettingsButtonPress, handleAdminButtonPress


async def handleButtonPress(u: Update, c):
    """Handles all the buttons presses / callback queries"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id

    query = u.callback_query
    queryData = query.data
    method = queryData.split()[0]

    isGroup = chatID != userID
    previewLink = False
    if isGroup:
        chat = db.getChat(chatID)
        previewLink = chat["settings"]["previewLink"]

    messageOwnerID = queryData.split()[-1]

    if (
        isGroup
        # naive way to check if it's a valid id ( Change it later )
        and messageOwnerID.isdigit()
        and len(messageOwnerID) >= 9
        and str(userID) != messageOwnerID
        and queryData.split()[0] not in "surahName prev next".split()
    ):
        return await query.answer(
            "Only the message owner can use this buttons", show_alert=True
        )

    if method == "settings":
        return await handleSettingsButtonPress(u, c)

    elif method == "admin":
        return await handleAdminButtonPress(u, c)

    elif method == "close":
        return await message.delete()

    elif method == "audio":
        try:
            surahNo, ayahNo = map(int, queryData.split()[1:-1])
        except ValueError:
            surahNo, ayahNo = map(int, queryData.split()[1:])

        await message.reply_audio(
            f"""https://quranaudio.pages.dev/{db.getUser(userID)["settings"]["reciter"]}/{
                surahNo}_{ayahNo}.mp3""",
            quote=True,
        )
        return await query.answer()

    elif method == "selectedSurah":
        surahNo = int(queryData.split()[1])

        entities = message.entities
        
        if len(entities) < 2: # When selected from searched surahs
            messageOwnerID = int(entities[0].url.split("/")[-1])
        else: # When selected from surahNames
            messageOwnerID = int(entities[1].url.split("/")[-1])
        
        if messageOwnerID != userID:
            return await query.answer(
                "Only the message owner can use this buttons", show_alert=True
            )

        surah = Quran.getSurahNameFromNumber(surahNo)
        await query.answer(f"You selected {surah}")

        reply = getAyahReplyFromPreference(surahNo, 1, userID)
        buttons = getAyahButton(surahNo, 1, userID)

    elif method in ("prev_page", "next_page"):
        # Going between surahNames Pages
        index = int(queryData.split()[1])
        if index > len(Constants.allSurahInlineButtons):
            index = 1

        url = message.entities
        messageOwnerID = int(url[1].url.split("/")[-1])
        if messageOwnerID != userID:
            return await query.answer(
                "Only the message owner can use this buttons", show_alert=True
            )

        reply = message.text_html
        buttons = InlineKeyboardMarkup(Constants.allSurahInlineButtons[index - 1])

    elif method == "prev_ayah":
        # Go to Previous Ayah
        values = queryData.split()[1:-1]

        if len(values) == 2:
            surahNo, ayahNo = map(int, values)
            language = None
        elif len(values) == 3:
            # language is the abbreviation of the language
            surahNo, ayahNo, language = map(int, values)

        if (
            surahNo == ayahNo == 1
        ):  # If the user is at the first ayah of the first surah
            surahNo = 114  # Go to the last surah
            ayahNo = 6

        elif ayahNo == 1:
            surahNo -= 1
            ayahNo = Quran.getAyahNumberCount(surahNo)
        else:
            ayahNo -= 1

        if language:
            reply = getAyahReply(surahNo, ayahNo, language)
        else:
            reply = getAyahReplyFromPreference(surahNo, ayahNo, userID)

        buttons = getAyahButton(surahNo, ayahNo, userID)

    elif method == "next_ayah":
        # Go to Next Ayah
        values = queryData.split()[1:-1]

        if len(values) == 2:
            surahNo, ayahNo = map(int, values)
            language = None

        elif len(values) == 3:
            # language is the abbreviation of the language
            surahNo, ayahNo, language = values
            surahNo = int(surahNo)
            ayahNo = int(ayahNo)


        if surahNo == 114 and ayahNo == 6:
            surahNo = 1
            ayahNo = 1

        elif ayahNo >= Quran.getAyahNumberCount(surahNo):
            surahNo += 1
            ayahNo = 1
        else:
            ayahNo += 1

        if language:
            reply = getAyahReply(surahNo, ayahNo, language)
            buttons = getAyahButton(surahNo, ayahNo, userID, language) # language is the abbr
        else:
            reply = getAyahReplyFromPreference(surahNo, ayahNo, userID)
            buttons = getAyahButton(surahNo, ayahNo, userID)

    await message.edit_text(
        reply, reply_markup=buttons, disable_web_page_preview=1 - previewLink
    )
