import html
import string

from telegram.ext import MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.database import db
from bot.handlers import Quran
from bot.handlers.helpers import getValidReply
from bot.handlers.message.replyToErrorMessage import replyToErrorMessage


ADMINS = db.admins


def escapeHTML(text: str):
    return html.escape(str(text))


async def handleMessage(u: Update, c):
    """Handles all the messages sent to the bot"""

    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text
    buttons = None

    if userID in ADMINS:  # Admins can reply to the error messages
        res = await replyToErrorMessage(u, c)
        if res:
            return

    if not text:
        return

    if text.startswith("/"):
        return  # Ignore commands

    x = getValidReply(userID, text)
    reply = x["text"]
    buttons = x["buttons"]

    if userID != chatID:
        chat = db.getChat(chatID)
        handleMessages = chat["settings"]["handleMessages"]
        previewLink = chat["settings"]["previewLink"]
        if buttons and handleMessages:
            await message.reply_html(
                reply,
                reply_markup=buttons,
                disable_web_page_preview=bool(1 - previewLink),
            )
        return  # Don't send the message to the group unless settings are enabled

    if (
        not x.get("send") and not buttons
    ):  # If the message is not valid and no buttons are there
        searchedSurah = checkSurah(userID, text)
        await message.reply_html(
            searchedSurah["reply"], reply_markup=searchedSurah["buttons"]
        )
        return

    await message.reply_html(reply, reply_markup=buttons)


def checkSurah(userID, text: str):
    defaultReply = f"""
Couldn't find a Surah matching the text <b>{escapeHTML(text)[:33]}{'...'if len(text) >= 33 else ''}</b>

<b>Write something like:
<blockquote>
fatihah
nas
baqarah
</blockquote>
</b>
"""


    res: list = Quran.searchSurah(text)
    if not res:
        return {"reply": defaultReply, "buttons": None}

    buttons = []
    for number, surah in res:
        buttons.append(
            InlineKeyboardButton(
                f"{number} {surah}", callback_data=f"selectedSurah {number}"
            )
        )

    buttons = InlineKeyboardMarkup([buttons])
    attachedUserID = f'<a href="https://xyz.co/{userID}"> </a>'  # Later used to check the message owner

    return {
        "reply": f"These{attachedUserID}are the surah that matches the most with the text you sent:",
        "buttons": buttons,
    }


exportedHandlers = [
    MessageHandler(filters.TEXT & ~filters.ChatType.CHANNEL, handleMessage)
]
