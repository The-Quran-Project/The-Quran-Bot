from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

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
    buttons = None

    if u.effective_message.via_bot:
        return

    if text.startswith("/"):
        return  # Ignore commands

    searchedSurah = checkSurah(u, c)

    if searchedSurah["buttons"]:
        reply = searchedSurah["reply"]
        buttons = searchedSurah["buttons"]
    else:
        x = getValidReply(userID, text)
        reply = x["text"]
        buttons = x["buttons"]

    if not buttons:  # Means the reply is invalid
        await message.reply_html(searchedSurah["reply"], quote=True)
        return
    await message.reply_html(reply, reply_markup=buttons, quote=True)


def checkSurah(u: Update, c):
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text

    defaultReply = f"""
Couldn't find a Surah matching the text <b>{escapeHTML(text)[:33]}{'...'if len(text) >= 33 else ''}</b>

<b>Write something like:
fatihah
nas
baqarah</b>
"""

    for i in text.lower().replace(" ", ""):
        if i not in string.ascii_lowercase:
            return {"reply": defaultReply, "buttons": None}

    res: list = Quran.searchSurah(text)
    if not res:
        return {"reply": defaultReply, "buttons": None}

    buttons = []
    for surah, number in res:
        buttons.append(
            InlineKeyboardButton(f"{number} {surah}", callback_data=f"surah {number}")
        )

    buttons = InlineKeyboardMarkup([buttons])

    return {
        "reply": "These are the surah that matches the most with the text you sent:",
        "buttons": buttons,
    }
