from telegram.ext import CallbackQueryHandler
from telegram import Update, Bot, InlineKeyboardMarkup, ChatPermissions


from .. import Quran
from .. import Constants
from ..database import db
from .handleSchedule import handleSchedule
from .handleAdminButtonPress import handleAdminButtonPress
from .handleSettingsButtonPress import handleSettingsButtonPress
from ..helpers import getAyahReply, getAyahReplyFromPreference, getAyahButton


async def handleButtonPress(u: Update, c):
    """Handles all the buttons presses / callback queries"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id

    query = u.callback_query
    queryData = query.data
    method = queryData.split()[0]
    reply = buttons = None

    isGroup = u.effective_chat.type in ("group", "supergroup")
    messageOwnerID = queryData.split()[-1]
    groupAnonymousBot = 1087968824

    valid_commands = ("surahName", "prev", "next")
    if (
        isGroup
        and messageOwnerID.isdecimal()
        and len(messageOwnerID) >= 9
        and int(messageOwnerID) != groupAnonymousBot
        and str(userID) != messageOwnerID
        and queryData.split()[0] not in valid_commands
    ):
        return await query.answer(
            "Only the message owner can use this buttons", show_alert=True
        )

    previewLink = False
    if isGroup:
        chat = db.getChat(chatID)
        previewLink = chat["settings"]["previewLink"]

    if method == "selectedSurah":
        surahNo = int(queryData.split()[1])

        entities = message.entities

        if len(entities) < 2:  # When selected from searched surahs
            messageOwnerID = int(entities[0].url.split("/")[-1])
        else:  # When selected from surahNames
            messageOwnerID = int(entities[1].url.split("/")[-1])

        if messageOwnerID != groupAnonymousBot and messageOwnerID != userID:
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
        if messageOwnerID != groupAnonymousBot and messageOwnerID != userID:
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
            surahNo, ayahNo, language = values
            surahNo = int(surahNo)
            ayahNo = int(ayahNo)

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
            buttons = getAyahButton(
                surahNo, ayahNo, userID, language
            )  # language is the abbr
        else:
            restrictedLangs = None
            if userID != chatID:
                restrictedLangs = db.getChat(chatID)["settings"]["restrictedLangs"]

            reply = getAyahReplyFromPreference(
                surahNo, ayahNo, userID, restrictedLangs=restrictedLangs
            )
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
            buttons = getAyahButton(
                surahNo, ayahNo, userID, language
            )  # language is the abbr
        else:
            restrictedLangs = None
            if userID != chatID:
                restrictedLangs = db.getChat(chatID)["settings"]["restrictedLangs"]

            reply = getAyahReplyFromPreference(
                surahNo, ayahNo, userID, restrictedLangs=restrictedLangs
            )
            buttons = getAyahButton(surahNo, ayahNo, userID)

    elif method == "audio":
        if u.effective_chat.type in ("group", "supergroup"):  # for groups
            permissions: ChatPermissions = await bot.getChatMember(chatID, bot.id)
            try:
                if (
                    not permissions.can_send_audios
                ):  # If the bot can't send audio messages
                    return await query.answer(
                        "I don't have permission to send audio messages in this group",
                        show_alert=True,
                    )
            except Exception as e:
                print(e)

            allowAudio = chat["settings"]["allowAudio"]
            if not allowAudio:
                return await query.answer(
                    "The admin has disabled audio recitations", show_alert=True
                )

        try:
            surahNo, ayahNo = map(int, queryData.split()[1:-1])
        except ValueError:
            surahNo, ayahNo = map(int, queryData.split()[1:])

        await message.reply_audio(
            f"""https://quranaudio.pages.dev/{db.getUser(userID)["settings"]["reciter"]}/{
                surahNo}_{ayahNo}.mp3"""
        )
        return await query.answer()

    if method == "settings":
        return await handleSettingsButtonPress(u, c)

    elif method == "admin":
        return await handleAdminButtonPress(u, c)

    elif method == "close":
        return await message.delete()

    elif method == "schedule":
        return await handleSchedule(u, c)

    if not reply:
        return await query.answer("Maybe it was an old message?", show_alert=True)

    await message.edit_text(
        reply, reply_markup=buttons, disable_web_page_preview=bool(1 - previewLink)
    )


exportedHandlers = [CallbackQueryHandler(handleButtonPress)]
