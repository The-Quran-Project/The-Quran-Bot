# pylint:disable=W0621
# pylint:disable=W0401
from telegram import *
from telegram.ext import *


import os
import time
import html
import string
import secrets

from uuid import uuid4
from ..quran import QuranClass
from ..utils import AyahNumberInvalid, SurahNumberInvalid
from .helpers import generateSurahButtons
from . import replies

Quran = QuranClass()


def escapeHTML(x):
    return html.escape(str(x))


class Constants:
    # --- Stickers ---
    salamSticker = (
        "CAACAgUAAxkBAAIBEGOtH-MLc6D7antAIRlma1YgnMe7AAJnBAAC3uq4VANpwAelURpaLAQ"
    )
    inShaAllah = (
        "CAACAgUAAxkBAAIBEWOtH-OoB2EaecZw_DAqRwvbHlOZAALWAwACkni4VLa6DL4cB1H6LAQ"
    )
    jazakAllah = (
        "CAACAgUAAxkBAAIBEmOtH-No3_xEGMh2YpM6ErBQ2BHHAAK4AwAC8Yq5VFbQH8fyZNceLAQ"
    )

    allSurahInlineButtons = generateSurahButtons(
        Quran
        # generates a 2D list of buttons for all the surahs
        # Each page contains 33 buttons (11 rows of 3 buttons each)
        # Eg. [[[button1], [button2], [button3]], [[button4], [button5], [button6]], ...]
        # | 1  | 2  | 3  |
        # | 4  | 5  | 6  |
        # | 7  | 8  | 9  |
        # | 10 | 11 | 12 |
        # | 13 | 14 | 15 |
        # | 16 | 17 | 18 |
        # | 19 | 20 | 21 |
        # | 22 | 23 | 24 |
        # | 25 | 26 | 27 |
        # | 28 | 29 | 30 |
        # | 31 | 32 | 33 |
        # | Prev | Next |
    )


async def startCommand(u: Update, c):
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    fn = u.effective_user.first_name
    url = "https://github.com/The-Quran-Project/TG-Quran-Bot"
    reply = replies.start.format(firstName=fn, repoURL=url)

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Github", url=url)]])
    x = await bot.sendSticker(chatID, Constants.salamSticker)
    await bot.sendMessage(
        chatID, reply, reply_to_message_id=x.message_id, reply_markup=buttons
    )


async def helpCommand(u: Update, c):
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    reply = replies.help

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Group", url="https://t.me/AlQuranDiscussion"),
                InlineKeyboardButton("Channel", url="https://t.me/AlQuranUpdates"),
            ]
        ]
    )

    await bot.sendMessage(chatID, reply, reply_markup=buttons)


async def useCommand(u: Update, c):
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    url = "https://telegra.ph/Al-Quran-05-29"
    reply = replies.howToUse.format(telegraphURL=url)

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Telegraph", url=url),
                InlineKeyboardButton(
                    "Try Inline Query", switch_inline_query_current_chat=f"1:2"
                ),
            ]
        ]
    )

    await bot.sendMessage(chatID, reply, reply_markup=buttons)


async def randomAyah(u: Update, c):
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    randSurah = secrets.randbelow(114) + 1  # number -> 1 to 114
    ayahCount = Quran.getAyahNumberCount(randSurah)
    randAyah = secrets.randbelow(ayahCount) + 1  # number -> 1 to `ayahCount``

    reply = _make_ayah_reply(randSurah, randAyah)
    buttons = _make_ayah_buttons(randSurah, randAyah)

    await bot.sendMessage(
        chatID, reply, reply_markup=buttons, reply_to_message_id=message.message_id
    )


# Helper Function: Checks Text and returns a valid reply
async def _giveValidReply(text):
    sep = text.split(":")
    if len(sep) != 2:
        reply = """
<b>Your format is not correct.</b>
Give like:

<pre>
surahNo : ayahNo
1:3
</pre>
"""
        reply = {"text": reply, "button": None}
        return reply

    surahNo, ayahNo = sep
    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdecimal() and ayahNo.isdecimal()):
        reply = """
<b>Surah and Ayah number must be integers</b>
Give like:
<pre>
surahNo : ayahNo
1:3
</pre>
"""

        reply = {"text": reply, "button": None}
        return reply

    surahNo = int(surahNo)

    if not 1 <= surahNo <= 114:
        reply = """
<b>Surah number needs to be between <i>1</i> to <i>114</i>.</b>
"""

        reply = {"text": reply, "button": None}
        return reply

    surah = Quran.getSurahNameFromNumber(surahNo)
    ayahCount = Quran.getAyahNumberCount(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= ayahNo <= ayahCount:
        reply = f"""
<b>Surah {surah} has {ayahCount} ayahs only.</b>

But you gave ayah no. {ayahNo}
"""

        reply = {"text": reply, "button": None}
        return reply

    reply = _make_ayah_reply(surahNo, ayahNo)

    button = _make_ayah_buttons(surahNo, ayahNo)

    reply = {"text": reply, "button": button}
    return reply


# Command:  /surah
async def surahCommand(u: Update, c):
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    fn = u.effective_user.first_name
    text = message.text[6:].strip()

    reply = """
<b>Select a surah from below:</b>
    """
    # Sends buttons with Surah names
    if not text:
        await bot.sendMessage(
            chatID,
            reply,
            reply_markup=InlineKeyboardMarkup(Constants.allSurahInlineButtons[0]),
        )
        return

    reply = await _giveValidReply(text)
    reply = reply["text"]
    button = reply["button"]

    await bot.sendMessage(
        chatID, reply, reply_to_message_id=message.message_id, reply_markup=button
    )


# Helper Function: Makes the buttons for Ayahs
def _make_ayah_buttons(surahNo: int or str, ayahNo: int or str, arabicStyle: int = 2):
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
                InlineKeyboardButton(
                    "Change Arabic Style",
                    callback_data=f"change-arabic  {surahNo} {ayahNo} {arabicStyle}",
                ),
                InlineKeyboardButton(
                    "Audio", callback_data=f"audio {surahNo} {ayahNo}"
                ),
            ],
        ]
    )

    return button


# Helper Function: Makes the reply for Ayahs
def _make_ayah_reply(surahNo: int or str, ayahNo: int or str, arabicStyle: int = 1):
    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)
    arabic = ayah.arabic if arabicStyle == 1 else ayah.arabic2

    reply = replies.sendAyahFull.format(
        surahName=surah,
        surahNo=surahNo,
        ayahNo=ayahNo,
        totalAyah=totalAyah,
        arabic=arabic,
        english=ayah.english,
        tafsir=ayah.tafsir,
    )

    return reply


async def surahCallback(u: Update, c):
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id
    query = u.callback_query
    query_data = query.data
    group = u.effective_chat.id != u.effective_user.id  # Checks if

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
        reply = _make_ayah_reply(index, 1)

        button = _make_ayah_buttons(index, 1)

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

        reply = _make_ayah_reply(surahNo, ayahNo)

        button = _make_ayah_buttons(surahNo, ayahNo)

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

        reply = _make_ayah_reply(surahNo, ayahNo)

        button = _make_ayah_buttons(surahNo, ayahNo)

        await edit_text(reply, reply_markup=button)

    # Toggling the style of Arabic.
    # Toggle between (with and without) harakat
    elif query_data.startswith("change-arabic"):
        surahNo, ayahNo, arabicStyle = map(int, query_data.split()[1:])

        surah = Quran.getSurahNameFromNumber(surahNo)
        toggle = {1: 2, 2: 1}
        reply = _make_ayah_reply(surahNo, ayahNo, arabicStyle)
        await edit_text(
            reply, reply_markup=_make_ayah_buttons(surahNo, ayahNo, toggle[arabicStyle])
        )

    elif query_data.startswith("audio"):
        surahNo, ayahNo = map(int, query_data.split()[1:])
        file_id = Quran.getAudioFile(surahNo, ayahNo)
        await bot.sendAudio(chatID, file_id, reply_to_message_id=message.message_id)
        await query.answer()


async def handleMessage(u: Update, c):
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text
    button = None
    group = u.effective_chat.id != u.effective_user.id

    if u.effective_message.via_bot:
        return

    if ":" not in text and not group:
        return await checkSurah(u, c)

    reply = await _giveValidReply(text)
    reply = reply["text"]
    button = reply["button"]
    webPreview = chatID != userID

    if not button and group:  # Means the reply is invalid
        return
    await bot.sendMessage(
        chatID,
        reply,
        reply_to_message_id=message.message_id,
        reply_markup=button,
        disable_web_page_preview=webPreview,
    )


async def checkSurah(u: Update, c):
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text

    if text.isdigit():
        surahNo = int(text)
        if not 1 <= surahNo <= 114:
            reply = """Surah number must be between 1-114"""
            await bot.sendMessage(chatID, reply, reply_to_message_id=message.message_id)
            return

        button = _make_ayah_buttons(surahNo, 1)

        reply = _make_ayah_reply(surahNo, 1)
        button = _make_ayah_buttons(surahNo, 1)
        await bot.sendMessage(
            chatID, reply, reply_to_message_id=message.message_id, reply_markup=button
        )

    for i in text.lower().replace(" ", ""):
        if i not in string.ascii_lowercase:
            return False

    res: list = Quran.searchSurah(text)
    if not res:
        reply = f"""
Couldn't find a Surah matching the text <b>{escapeHTML(text)}</b>

Write something like:
fatihah
nas
"""
        await bot.sendMessage(chatID, reply, reply_to_message_id=message.message_id)
        return False

    buttons = []
    for surah, number in res:
        buttons.append(
            InlineKeyboardButton(f"{number} {surah}", callback_data=f"surah {number}")
        )

    buttons = InlineKeyboardMarkup([buttons])

    await bot.sendMessage(
        chatID,
        "These are the surah that matches the most with the text you sent:",
        reply_to_message_id=message.message_id,
        reply_markup=buttons,
    )

    return True


# Inline Query Handler
async def handleInlineQuery(u: Update, c):
    query = u.inline_query.query
    inQuery = InlineQueryResultArticle
    if not query:
        return

    if ":" not in query:
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>",
            )
        ]
        await u.inline_query.answer(res)
        return

    sep = query.split(":")
    if "" in sep:
        sep.remove("")

    if len(sep) < 2:
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>",
            )
        ]
        await u.inline_query.answer(res)
        return

    surahNo, ayahNo, *ext = sep

    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdigit() and ayahNo.isdigit()):
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="SurahNo and AyahNo must be numbers.",
            )
        ]
        await u.inline_query.answer(res)
        return

    surahNo = int(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= surahNo <= 144:
        res = [
            inQuery(
                id=uuid4(),
                title="Surah Not Valid",
                input_message_content=InputTextMessageContent(
                    "Surah Number must be between 1 114\nFormat: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="Surah Number not Valid",
            )
        ]
        await u.inline_query.answer(res)
        return

    ayahCount = Quran.getAyahNumberCount(surahNo)

    if not 1 <= ayahNo <= ayahCount:
        res = [
            inQuery(
                id=uuid4(),
                title="Ayah Not Valid",
                input_message_content=InputTextMessageContent(
                    f"Surah {Quran.getSurahNameFromNumber(surahNo)} has {ayahCount} ayahs only."
                ),
                description=f"Surah {Quran.getSurahNameFromNumber(surahNo)} has {ayahCount} ayahs only.",
            )
        ]
        await u.inline_query.answer(res)
        return

    try:
        ext: str = ext[0].strip().lower()
        if ext == "1":
            arabicStyle = 1

    except IndexError:
        arabicStyle = 2

    surahName = Quran.getSurahNameFromNumber(surahNo)
    reply = _make_ayah_reply(surahNo, ayahNo, arabicStyle)
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Try Inline Query",
                    switch_inline_query_current_chat=f"{surahNo}:{ayahNo}",
                )
            ]
        ]
    )
    res = [
        inQuery(
            id=f"{surahNo}:{ayahNo}",
            title=surahName,
            input_message_content=InputTextMessageContent(
                reply, disable_web_page_preview=True
            ),
            description=f"{surahNo}. {surahName} ({ayahNo})",
            thumbnail_url="https://graph.org/file/728d9dda8867352e06707.jpg",
            reply_markup=buttons,
        )
    ]

    await u.inline_query.answer(res)
