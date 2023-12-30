from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from .helpers import getRandomAyah, getValidReply
from . import Constants, replies


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

    reply = await getValidReply(text)
    reply = reply["text"]
    button = reply["button"]

    await bot.sendMessage(
        chatID, reply, reply_to_message_id=message.message_id, reply_markup=button
    )


async def randomCommand(u: Update, c):
    bot: Bot = c.bot
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    mid = u.effective_message.message_id

    x = getRandomAyah(userID)
    reply = x["reply"]
    button = x["button"]

    await bot.sendMessage(chatID, reply, reply_markup=button, reply_to_message_id=mid)
