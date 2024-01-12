from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

import html
import string

from .helpers import getValidReply, getAyahReply, getAyahButton
from . import Quran


def escapeHTML(text: str):
    return html.escape(str(text))


async def handleMessage(u: Update, c):
    """Handles all the messages sent to the bot"""
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

    x = getValidReply(userID, text)
    reply = x["text"]
    button = x["button"]
    webPreview = chatID != userID

    if not button and group:  # Means the reply is invalid
        return
    await message.reply_html(
        reply, reply_markup=button, quote=True, disable_web_page_preview=webPreview
    )


async def checkSurah(u: Update, c):
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text

    if text.isdigit():
        surahNo = int(text)
        if not 1 <= surahNo <= 114:
            reply = """Surah number must be between 1-114"""
            await message.reply_html(reply, reply_markup=button, quote=True)
            return

        button = getAyahButton(surahNo, 1)

        reply = getAyahReply(userID, surahNo, 1)
        button = getAyahButton(surahNo, 1)
        await message.reply_html(reply, reply_markup=button, quote=True)
        return

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
baqarah
"""
        await message.reply_html(reply, reply_markup=button, quote=True)
        return False

    buttons = []
    for surah, number in res:
        buttons.append(
            InlineKeyboardButton(f"{number} {surah}", callback_data=f"surah {number}")
        )

    buttons = InlineKeyboardMarkup([buttons])

    await message.reply_html(
        "These are the surah that matches the most with the text you sent:",
        reply_markup=button,
        quote=True,
    )

    return True
