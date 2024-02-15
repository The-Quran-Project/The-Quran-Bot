from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from .helpers import getRandomAyah, getValidReply
from . import Constants, replies
from . import Quran
from .database import db


# Command:  /start
async def startCommand(u: Update, c):
    """Sends a welcome message to the user and a link to the repo"""
    message = u.effective_message
    fn = u.effective_user.first_name
    url = "https://github.com/The-Quran-Project/TG-Quran-Bot"
    reply = replies.start.format(firstName=fn, repoURL=url)

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Github", url=url)]])
    msg = await message.reply_sticker(Constants.salamSticker)
    await msg.reply_html(reply, reply_markup=buttons)


# Command:  /help
async def helpCommand(u: Update, c):
    """Sends a help message to the user"""
    message = u.effective_message
    reply = replies.help

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Group", url="https://t.me/AlQuranDiscussion"),
                InlineKeyboardButton("Channel", url="https://t.me/AlQuranUpdates"),
            ]
        ]
    )

    await message.reply_html(reply, reply_markup=buttons)


# Command:  /about
async def aboutCommand(u: Update, c):
    """Sends an about message to the user"""
    message = u.effective_message
    reply = replies.about

    await message.reply_html(reply)


# Command:  /use
async def useCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
    message = u.effective_message
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

    await message.reply_html(reply, reply_markup=buttons)


# Command:  /surah
async def surahCommand(u: Update, c):
    """Sends a list of all the Surahs to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[6:].strip()  # 6 is the length of "/surah"

    reply = """
<b>Select a surah from below:</b>
    """
    # Sends buttons with Surah names
    if not text:
        buttons = Constants.allSurahInlineButtons[0]
        await message.reply_html(reply, reply_markup=InlineKeyboardMarkup(buttons))
        return

    x = getValidReply(userID, text)
    reply = x["text"]
    buttons = x["buttons"]

    msg: Message = await message.reply_html(reply, reply_markup=buttons)

    # await msg.reply_html(


#        "<b>Use of <code>/surah x:y</code> is deprecated and will be removed in/after 1st July, 2024</b>\n\nUse <code>/get x:y</code> instead",
#        quote=True,
#    )


# Command:  /get
async def getCommand(u: Update, c):
    """Sends the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[4:].strip()  # 4 is the length of "/get"

    x = getValidReply(userID, text)
    reply = x["text"]
    buttons = x["buttons"]

    await message.reply_html(reply, reply_markup=buttons)


# Command: /get<language>
async def getWithLanguage(u: Update, c):
    """Sends the ayah to the user in the specified language"""
    message = u.effective_message
    userID = u.effective_user.id
    # 4 to 6 will be the language code (e.g. /getar)
    language = message.text[4:6].lower()
    text = message.text[6:].strip()  # 6 is the length of "/get<language>"
    newLine = "\n"
    if language not in Constants.languages:
        reply = f"""
<b>Language code is not valid</b>

Use one of the following:
{"-"+newLine.join(Constants.languages)}

Give such as:
<pre>
/getar 1:3
/geten 3:5
</pre>
"""
        await message.reply_html(reply)
        return

    x = getValidReply(userID, text, language)
    reply = x["text"]
    buttons = x["buttons"]

    await message.reply_html(reply, reply_markup=buttons)


# Command:  /random or /rand
async def randomCommand(u: Update, c):
    """Sends a random Ayah to the user"""
    userID = u.effective_user.id
    message = u.effective_message

    x = getRandomAyah(userID)
    reply = x["reply"]
    buttons = x["buttons"]

    await message.reply_html(reply, reply_markup=buttons)


# Command:  /audio
async def audioCommand(u: Update, c):
    """Sends the audio of the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[6:].strip()  # 6 is the length of "/audio"

    x = getValidReply(userID, text)
    buttons = x["buttons"]

    if not buttons:
        await message.reply_html(x["text"])
        return

    if ":" not in text != 2:
        text += ":1"
    surah, ayah = text.split(":")
    surah = surah.strip()
    ayah = ayah.strip()

    await message.reply_audio(
        f"""https://quranaudio.pages.dev/{db.getUser(userID)["settings"]["reciter"]}/{
            surah}_{ayah}.mp3""",
        quote=True,
    )


# Command:  /tafsir
async def tafsirCommand(u: Update, c):
    """Sends the tafsir of the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[7:].strip()  # 7 is the length of "/tafsir"

    x = getValidReply(userID, text)
    buttons = x["buttons"]

    if not buttons:
        await message.reply_html(x["text"])
        return

    if ":" not in text != 2:
        text += ":1"
    surah, ayah = text.split(":")
    surah = surah.strip()
    ayah = ayah.strip()

    tafsir = Quran.getAyah(surah, ayah).tafsir
    await message.reply_html(
        f"<b>Tafsir:</b> <a href='{tafsir}'>Telegraph</a>", quote=True
    )
