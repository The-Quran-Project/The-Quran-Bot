from telegram.ext import CallbackQueryHandler
from telegram import (
    InlineKeyboardButton,
    InputMediaAudio,
    Update,
    Bot,
    InlineKeyboardMarkup,
    ChatPermissions,
)


from bot.handlers import Quran
from bot.handlers.helpers import getPrevAyah, getNextAyah, getNextSurah, getPrevSurah
from bot.handlers import Constants
from bot.handlers.localDB import db
from bot.handlers.callbackQuery.handleSchedule import handleSchedule
from bot.handlers.callbackQuery.handleAdminButtonPress import handleAdminButtonPress
from bot.handlers.callbackQuery.handleSettingsButtonPress import (
    handleSettingsButtonPress,
)
from bot.handlers.helpers import (
    getAudioUrlOrID,
    getAyahReply,
    getAyahReplyFromPreference,
    getAyahButton,
)
from bot.utils import getLogger

logger = getLogger(__name__)


async def handleButtonPress(u: Update, c):
    """Handles all the buttons presses / callback queries"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    forceUrl = bot.username != Constants.botUsername
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
        chat = db.chats.get(chatID)
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

    elif method == "prev_ayah" or method == "next_ayah":
        # Extract parameters from callback data
        values = queryData.split()[1:-1]
        language = None

        # Parse surah and ayah (and language if provided)
        if len(values) == 2:
            surahNo, ayahNo = map(int, values)
        else:
            surahNo, ayahNo, language = values
            surahNo, ayahNo = int(surahNo), int(ayahNo)

        # Determine next or previous ayah
        if method == "prev_ayah":
            surahNo, ayahNo = getPrevAyah(surahNo, ayahNo)
        else:
            surahNo, ayahNo = getNextAyah(surahNo, ayahNo)

        # Get ayah reply and buttons (based on language or user preferences)
        if language:
            reply = getAyahReply(surahNo, ayahNo, language)
            buttons = getAyahButton(surahNo, ayahNo, userID, language)
        else:
            restrictedLangs = None
            if userID != chatID:
                restrictedLangs = db.chats.get(chatID)["settings"]["restrictedLangs"]

            reply = getAyahReplyFromPreference(
                surahNo, ayahNo, userID, restrictedLangs=restrictedLangs
            )
            buttons = getAyahButton(surahNo, ayahNo, userID)

    elif method == "prev_audio" or method == "next_audio":
        # Extract parameters from callback data
        values = queryData.split()[1:-1]
        surahNo, ayahNo, reciter, onlySurah = map(int, values)

        # Determine next or previous audio
        if method == "prev_audio":
            if onlySurah:
                surahNo = getPrevSurah(surahNo)
            else:
                surahNo, ayahNo = getPrevAyah(surahNo, ayahNo)
        else:
            if onlySurah:
                surahNo = getNextSurah(surahNo)
            else:
                surahNo, ayahNo = getNextAyah(surahNo, ayahNo)

        # Edit the audio message with the new audio
        urlOrFileID = getAudioUrlOrID(
            surahNo, ayahNo, reciter, onlySurah=onlySurah, forceUrl=forceUrl
        )
        audioNavigation = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Previous",
                        callback_data=f"prev_audio {surahNo} {ayahNo} {reciter} {onlySurah} {userID}",
                    ),
                    InlineKeyboardButton(
                        "Next",
                        callback_data=f"next_audio {surahNo} {ayahNo} {reciter} {onlySurah} {userID}",
                    ),
                ],
            ]
        )

        if onlySurah:
            caption = f"<b>Audio of Surah <code>{surahNo}</code></b>"
        else:
            caption = f"<b>Audio of:</b> <code>{surahNo}:{ayahNo}</code>"
        try:
            await message.edit_media(
                media=InputMediaAudio(
                    media=urlOrFileID,
                    caption=caption,
                ),
                reply_markup=audioNavigation,
            )
        except Exception as e:
            # If editing fails, send as a new message
            await message.reply_audio(
                audio=urlOrFileID,
                caption="<b>Message Edit Failed</b>\n" + caption,
                reply_markup=audioNavigation,
            )
            raise Exception(f"Error editing media: {e}")
        return await query.answer()

    # ---------------------------------------------------------------------

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
                logger.error(f"In audio button: {e}")

            allowAudio = chat["settings"]["allowAudio"]
            if not allowAudio:
                return await query.answer(
                    "The admin has disabled audio recitations", show_alert=True
                )

        try:
            surahNo, ayahNo = map(int, queryData.split()[1:-1])
        except ValueError:
            surahNo, ayahNo = map(int, queryData.split()[1:])

        user = db.users.get(userID)
        if user:
            reciter = user["settings"]["reciter"]
        else:
            reciter = 1

        urlOrFileID = getAudioUrlOrID(surahNo, ayahNo, reciter, forceUrl=forceUrl)

        audioNavigation = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Previous",
                        callback_data=f"prev_audio {surahNo} {ayahNo} {reciter} {userID}",
                    ),
                    InlineKeyboardButton(
                        "Next",
                        callback_data=f"next_audio {surahNo} {ayahNo} {reciter} {userID}",
                    ),
                ],
            ]
        )

        caption = f"<b>Audio of:</b> <code>{surahNo}:{ayahNo}</code>"

        await message.reply_audio(
            urlOrFileID, reply_markup=audioNavigation, caption=caption
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
