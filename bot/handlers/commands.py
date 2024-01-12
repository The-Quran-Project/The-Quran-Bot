from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from .helpers import getRandomAyah, getValidReply
from . import Constants, replies

# ---------------------------------------- #
# ------------ Other Commands ------------ #
from .others import (
    pingCommand,
    infoCommand,
)
# ---------------------------------------- #




# Command:  /start
async def startCommand(u: Update, c):
    """Sends a welcome message to the user and a link to the repo"""
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    fn = u.effective_user.first_name
    url = "https://github.com/The-Quran-Project/TG-Quran-Bot"
    reply = replies.start.format(firstName=fn, repoURL=url)

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Github", url=url)]])
    x = await bot.sendSticker(chatID, Constants.salamSticker)
    await bot.sendMessage(
        chatID, reply, reply_to_message_id=x.message_id, reply_markup=buttons, message_thread_id=u.effective_message.message_thread_id
    )


# Command:  /help
async def helpCommand(u: Update, c):
    """Sends a help message to the user"""
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    reply = replies.help

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Group", url="https://t.me/AlQuranDiscussion"),
                InlineKeyboardButton(
                    "Channel", url="https://t.me/AlQuranUpdates"),
            ]
        ]
    )

    await bot.sendMessage(chatID, reply, reply_markup=buttons, message_thread_id=u.effective_message.message_thread_id)


# Command:  /about
async def aboutCommand(u: Update, c):
    """Sends an about message to the user"""
    bot: Bot = c.bot
    chatID = u.effective_chat.id
    reply = replies.about

    await bot.sendMessage(chatID, reply, message_thread_id=u.effective_message.message_thread_id)


# Command:  /use
async def useCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
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

    await bot.sendMessage(chatID, reply, reply_markup=buttons, message_thread_id=u.effective_message.message_thread_id)


# Command:  /surah
async def surahCommand(u: Update, c):
    """Sends a list of all the Surahs to the user"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text[6:].strip()

    reply = """
<b>Select a surah from below:</b>
    """
    # Sends buttons with Surah names
    if not text:
        await bot.sendMessage(
            chatID,
            reply,
            reply_markup=InlineKeyboardMarkup(
                Constants.allSurahInlineButtons[0]),
            message_thread_id=u.effective_message.message_thread_id
        )
        return

    x = getValidReply(userID, text)
    reply = x["text"]
    button = x["button"]

    x = await bot.sendMessage(
        chatID, reply, reply_to_message_id=message.message_id, reply_markup=button, message_thread_id=u.effective_message.message_thread_id
    )
    await bot.sendMessage(chatID, "<b>Use of <code>/surah x:y</code> is deprecated and will be removed in 1st July, 2024</b>\n\nUse <code>/get x:y</code> instead", reply_to_message_id=x.message_id, message_thread_id=u.effective_message.message_thread_id)


# Command:  /get
async def get(u: Update, c):
    """Sends the ayah to the user"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text[5:].strip()

    x = getValidReply(userID, text)
    reply = x["text"]
    button = x["button"]

    x = await bot.sendMessage(
        chatID, reply, reply_to_message_id=message.message_id, reply_markup=button, message_thread_id=u.effective_message.message_thread_id
    )


# Command: /get<language>
async def getWithLanguage(u: Update, c):
    """Sends the ayah to the user in the specified language"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text[5:].strip()

    x = getValidReply(userID, text)
    reply = x["text"]
    button = x["button"]

    x = await bot.sendMessage(
        chatID, reply, reply_to_message_id=message.message_id, reply_markup=button, message_thread_id=u.effective_message.message_thread_id
    )


# Command:  /random or /rand
async def randomCommand(u: Update, c):
    """Sends a random Ayah to the user"""
    bot: Bot = c.bot
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    mid = u.effective_message.message_id

    x = getRandomAyah(userID)
    reply = x["reply"]
    button = x["button"]

    await bot.sendMessage(chatID, reply, reply_markup=button, reply_to_message_id=mid, message_thread_id=u.effective_message.message_thread_id)
