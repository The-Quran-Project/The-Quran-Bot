import regex

from ..database import db
from .. import Quran
from ..helpers.decorators import onlyGroupAdmin

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes


def _addScheduleToTemp(chatID: int, time: dict, chatType: str, langs: list = None):
    """Add a schedule to the temp database."""
    langs = [i for i in langs if i] or ["english_1"]
    collection = db.db.schedules
    return collection.update_one(
        {"_id": chatID},
        {
            "$set": {
                "time": time,
                "chatType": chatType,
                "langs": langs,
                "enabled": True,
            }
        },
        upsert=True,
    )


__length = len("/schedule ")

validMethod = """\
<b><u>Examples:</u></b>
<code>/schedule 11:49 pm</code>
<code>/schedule 11:49 am</code>
<code>/schedule 23:49</code> (24-hour format)

<b><i>Note:</i></b>
Spaces doesn't matter.
<code>11 : 49 pm</code> is same as <code>11:49pm</code>"""


pattern = regex.compile(
    r"^(?P<hour>\d{1,2})\s*:\s*(?P<minute>\d{1,2})\s*(?P<ampm>[ap]\s*m)?\s*(-\s*(?P<langs>[a-z]{3}(?:\s+[a-z]{3})*))?$",
    regex.IGNORECASE,
)  # Match for: 11:49 pm - eng ara tur {'hour': '11', 'minute': '49', 'ampm': 'pm', 'langs': 'eng ara tur'}

# TODO: run repeating every minute to check if the time has come
# Enable, Disable, Delete schedule


# /schedule 11:49 pm - eng ara
@onlyGroupAdmin
async def scheduleCommand(u: Update, c: ContextTypes.DEFAULT_TYPE):
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    splitted = message.text[__length:].lower().split("-")
    text = splitted[0].strip()
    langs = splitted[1].split() if len(splitted) > 1 else []

    if not text:
        return await showSchedule(u, c)

    result = await _validateTime(message, text)
    if not result:
        return

    langs = [Quran.detectLanguage(i) for i in langs]
    languages = [str(Quran.getTitleLanguageFromLang(i)) for i in langs]

    msg = f"""
<b>Schedule Enabled</b>
A random verse will be sent at the following time:

<b>Time:</b> {result["hour"]:02d}:{result["minute"]:02d} UTC (24-hour format)

<b>Language:</b> {", ".join(languages) or "English"}

{any(lang == None for lang in languages) and "<i>Invalid language(s) will be ignored.</i>" or ""}
"""
    buttons = [
        [
            InlineKeyboardButton("Delete", callback_data="schedule delete"),
            InlineKeyboardButton("Disable", callback_data="schedule disable"),
            # InlineKeyboardButton("Enable", callback_data="schedule enable"),
        ],
        [
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ]

    if u.channel_post:
        # if previously scheduled, cancel the job
        _addScheduleToTemp(chatID, result, chatType="channel", langs=langs)

    elif u.effective_chat.type in "private":
        _addScheduleToTemp(chatID, result, chatType="private", langs=langs)
    else:
        _addScheduleToTemp(chatID, result, chatType="group", langs=langs)

    await message.reply_html(msg, reply_markup=InlineKeyboardMarkup(buttons))


async def showSchedule(u: Update, c: ContextTypes.DEFAULT_TYPE):
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    collection = db.db.schedules
    data = collection.find_one({"_id": chatID})
    if not data:
        return await message.reply_html(
            "No schedule found. See /help for more information."
        )

    time = data.get("time")
    langs = data.get("langs")
    chatType = data.get("chatType")
    enabled = data.get("enabled")

    languages = [str(Quran.getTitleLanguageFromLang(i)) for i in langs]

    msg = f"""
<b>Schedule Information</b>
A random verse will be sent at the following time:

<b>Time:</b> {time["hour"]:02d}:{time["minute"]:02d} UTC (24-hour format)

<b>Languages:</b> <code>{", ".join(languages) or "English"}</code>
<b>Status:</b> <i>{"Enabled" if enabled else "Disabled"}</i>
<b>Chat ID:</b> <code>{chatID}</code>
<b>Chat Type:</b> {chatType.capitalize()}
"""
    buttons = [
        [
            InlineKeyboardButton("Disable", callback_data="schedule disable"),
            InlineKeyboardButton("Enable", callback_data="schedule enable"),
        ],
        [
            InlineKeyboardButton("Delete", callback_data="schedule delete"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ]

    await message.reply_html(msg, reply_markup=InlineKeyboardMarkup(buttons))


async def _validateTime(message, text: str):
    """Validate the time format and return the time in 24-hour format."""
    match = pattern.match(text)
    if not match:
        msg = f"""
<b>Invalid time format.</b>

{validMethod}
"""
        await message.reply_html(msg)
        return False

    data = match.groupdict()
    hour = int(data["hour"])
    minute = int(data["minute"])
    ampm = data["ampm"] and data["ampm"].strip().lower() or None

    if ampm and hour > 12:
        msg = f"""
<b>Invalid time format.</b>
Hour should be less than 12 when using AM/PM format.

{validMethod}
"""
        await message.reply_html(msg)
        return False

    if minute > 59:
        msg = f"""
<b>Invalid time format.</b>
Minute should be less than 60.

{validMethod}
"""
        await message.reply_html(msg)
        return False

    if ampm:
        if ampm == "pm":
            if hour < 12:
                hour += 12
        else:
            if hour >= 12:
                hour -= 12

    return {"hour": hour, "minute": minute}


exportedHandlers = [
    MessageHandler(filters.Regex(r"^/schedule"), scheduleCommand),
]
