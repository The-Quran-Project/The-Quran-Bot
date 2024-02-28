import html

from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from . import Quran
from .database import db
from . import Constants, replies
from .helpers import getRandomAyah, getValidReply


def escapeHTML(text: str) -> str:
    return html.escape(str(text))


# Command:  /start
async def startCommand(u: Update, c):
    """Sends a welcome message to the user and a link to the repo"""
    message = u.effective_message
    chatID = u.effective_chat.id
    userID = u.effective_user.id
    fn = u.effective_user.first_name
    url = "https://github.com/The-Quran-Project/The-Quran-Bot"
    reply = replies.start.format(firstName=escapeHTML(fn), repoURL=url)

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Github", url=url)]])

    msg: Message = message
    if chatID == userID:  # Send sticker only if it's a private chat
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
    attachedUserID = f'<a href="https://xyz.co/{userID}"> </a>'  # Later used to check the message owner

    reply = f"""
<b>Select a surah{attachedUserID}from below:</b>
    """
    # Sends buttons with Surah names
    if not text:
        buttons = Constants.allSurahInlineButtons[0]
        await message.reply_html(reply, reply_markup=InlineKeyboardMarkup(buttons))
        return

    x = getValidReply(userID, text)
    reply = x["text"]
    buttons = x["buttons"]

    await message.reply_html(reply, reply_markup=buttons)


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


# Command:  /<lang> x:y
async def getTranslationCommand(u: Update, c):
    """Sends the ayah in the specified language to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[1:].strip()  # 1 is the length of "/"

    lang, text = text.split(" ", 1)
    if len(lang) < 2:
        return

    language = Quran.detectLanguage(lang)

    if not language:
        return
        availableLanguages = [i[1] for i in Quran.getLanguages()]
        reply = f"""
<b>❌ Invalid Language ❌</b>

If you want to suggest a language, please say it in the <a href="https://t.me/AlQuranDiscussion">discussion group</a>.

Available languages are:
<blockquote>\
{', '.join(availableLanguages)}
</blockquote>
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
            surah}_{ayah}.mp3"""
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
    await message.reply_html(f"<b>Tafsir:</b> <a href='{tafsir}'>Telegraph</a>")


# Command:  /translations
async def translationsCommand(u: Update, c):
    """Sends the list of all the available translations to the user"""
    message = u.effective_message
    reply = f"""
<b>Available Translations:</b>

<blockquote>\
{', '.join([i[1] for i in Quran.getLanguages()])}
</blockquote>
"""
    await message.reply_html(reply)
