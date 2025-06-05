import html

from telegram.ext import CommandHandler, MessageHandler, filters
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup


from bot.handlers.database import db
from bot.handlers import Quran
from bot.handlers import Constants, replies
from bot.handlers.helpers import (
    getRandomAyah,
    getValidReply,
    getSurahAudio,
    isValidFormat,
    getAyahButton,
)


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

    if u.effective_chat.type == "private":  # Send sticker only if it's a private chat
        message = await message.reply_sticker(Constants.salamSticker)

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


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

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


# Command:  /about
async def aboutCommand(u: Update, c):
    """Sends an about message to the user"""
    message = u.effective_message
    reply = replies.about

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(reply, disable_web_page_preview=disablePreviewForGroups)


# Command:  /use
async def useCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
    message = u.effective_message
    url = "https://telegra.ph/Al-Quran-05-29"  # old
    url = "https://telegra.ph/Usage-of-Quran-Bot-04-19"
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

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


# Command:  /surah
async def surahCommand(u: Update, c):
    """Sends a list of all the Surahs to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
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

    restrictedLangs = None
    # previewLink = True
    if userID != chatID:
        settings = db.getChat(chatID)["settings"]
        restrictedLangs = settings["restrictedLangs"]
        # previewLink = settings["previewLink"]

    x = getValidReply(userID, text, restrictedLangs=restrictedLangs)
    reply = x["text"]
    buttons = x["buttons"]

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_notification=disablePreviewForGroups
    )


# Command:  /get
async def getCommand(u: Update, c):
    """Sends the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text[4:].strip()  # 4 is the length of "/get"

    restrictedLangs = None
    # previewLink = True
    if userID != chatID:
        settings = db.getChat(chatID)["settings"]
        restrictedLangs = settings["restrictedLangs"]
        # previewLink = settings["previewLink"]

    x = getValidReply(userID, text, restrictedLangs=restrictedLangs)
    reply = x["text"]
    buttons = x["buttons"]
    if not buttons and userID != chatID:
        return

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_notification=disablePreviewForGroups
    )


# Command:  /<lang> x:y
async def getTranslationCommand(u: Update, c):
    """Sends the ayah in the specified language to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    text = message.text[1:].strip()  # 1 is the length of "/"

    lang, text = text.split(" ", 1)
    if len(lang) < 2:
        return

    language = Quran.detectLanguage(lang)

    if not language:
        if userID != chatID:
            return
        availableLanguages = [i[1] for i in Quran.getLanguages()]
        reply = f"""
<b>❌ Invalid Language ❌</b>

Available languages are:
<blockquote>\
{', '.join(availableLanguages)}
</blockquote>

You can also use the language abbr. For example,
<code>en</code> for English
<code>en2</code> for Mufti Taqi Usmani
<code>ar</code> for Arabic

If you want to use a language that is not listed, please suggest it in the <a href="https://t.me/AlQuranDiscussion">discussion group</a>.
"""
        await message.reply_html(reply)
        return

    x = getValidReply(userID, text, language)
    reply = x["text"]
    buttons = x["buttons"]

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


# Command:  /random or /rand
async def randomCommand(u: Update, c):
    """Sends a random Ayah to the user"""
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    message = u.effective_message

    x = getRandomAyah(userID)
    reply = x["reply"]
    buttons = x["buttons"]

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


# Command:  /audio
async def audioCommand(u: Update, c):
    """Sends the audio of the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[6:].strip()  # 6 is the length of "/audio"

    x = isValidFormat(text)
    ok = x["ok"]
    if not ok:
        await message.reply_html(x["message"])
        return

    onlySurah = x.get("onlySurah")  # True if only Surah is provided
    surahNo = x["surahNo"]
    ayahNo = x["ayahNo"]

    if onlySurah:
        if 1 == 2 and userID != 5596148289:
            await message.reply_html(
                "<b>Developer currently disabled this feature because of some problems, it'll be back soon</b>\nStay updated with @AlQuranUpdates"
            )
            return

        audioFileID = getSurahAudio(surahNo, userID)
        await message.reply_audio(audioFileID)
        return

    preferredReciter = db.getUser(userID)["settings"]["reciter"]

    await message.reply_audio(
        f"""https://quranaudio.pages.dev/{preferredReciter}/{
            surahNo}_{ayahNo}.mp3"""
    )


# Command:  /tafsir
async def tafsirCommand(u: Update, c):
    """Sends the tafsir of the ayah to the user"""
    message = u.effective_message
    userID = u.effective_user.id
    text = message.text[7:].strip()  # 7 is the length of "/tafsir"

    x = isValidFormat(text)
    if x["ok"] == False:
        await message.reply_html(x["message"])
        return

    surahNo = x["surahNo"]
    ayahNo = x["ayahNo"]
    buttons = getAyahButton(surahNo, ayahNo, userID)
    tafsir = Quran.getAyah(surahNo, ayahNo).tafsir
    reply = f"<b>Tafsir:</b> <a href='{tafsir}'>Telegraph</a>"

    disablePreviewForGroups = False
    if u.effective_chat.type in ("group", "supergroup"):
        disablePreviewForGroups = True

    await message.reply_html(
        reply, reply_markup=buttons, disable_web_page_preview=disablePreviewForGroups
    )


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


exportedHandlers = [
    CommandHandler("start", startCommand),
    CommandHandler("help", helpCommand),
    CommandHandler("about", aboutCommand),
    CommandHandler("use", useCommand),
    CommandHandler("surah", surahCommand),
    CommandHandler("get", getCommand),
    CommandHandler("audio", audioCommand),
    CommandHandler("tafsir", tafsirCommand),
    CommandHandler("translations", translationsCommand),
    CommandHandler("random", randomCommand),
    CommandHandler("rand", randomCommand),
    CommandHandler("langs", translationsCommand),
    CommandHandler("languages", translationsCommand),
    MessageHandler(
        (~filters.ChatType.CHANNEL)
        & filters.Regex(
            r"^\/([A-Za-z0-9]{1,10})\s\d+\s?:*\s?\d*$"
        ),  # match: /<lang> <surah>:<ayah> or /<lang> <surah>
        getTranslationCommand,
    ),
]
