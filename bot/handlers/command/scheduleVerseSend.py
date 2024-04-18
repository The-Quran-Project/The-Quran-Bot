import regex

from ..database import db
from ...quran import QuranClass
from ..helpers.decorators import onlyGroupAdmin

from telegram import Update, Bot
from telegram.ext import MessageHandler, filters, ContextTypes


def _addSchedule(chatID: int, time: dict, chatType: str):
    callbacks = {
        "group": {"get": db.getChat, "add": db.addChat, "update": db.updateChat},
        "channel": {
            "get": db.getChannel,
            "add": db.addChannel,
            "update": db.updateChannel,
        },
        "private": {"get": db.getUser, "add": db.addUser, "update": db.updateUser},
    }

    if chatType in callbacks:
        entity = callbacks[chatType]["get"](chatID)
        if not entity:
            entity = callbacks[chatType]["add"](chatID)

        entity["settings"]["schedule"] = {
            **time,
            "job": None,
        }
        callbacks[chatType]["update"](chatID, entity["settings"])


# /schedule 11:49 pm

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
    r"^(?P<hour>\d{1,2})\s*:\s*(?P<minute>\d{1,2})\s*(?P<ampm>[ap]\s*m)?$",
    regex.IGNORECASE,
)

# TODO: run repeating every minute to check if the time has come

# /schedule 11:49 pm - eng, ara
@onlyGroupAdmin
async def scheduleCommand(u: Update, c:ContextTypes.DEFAULT_TYPE):
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    text = message.text[__length:].replace(" ", "").lower()
    result = await _validateTime(message, text)
    if not result:
        return

    msg = f"""
<b>Scheduled successfully.</b>
A random verse will be sent at the following time:

<b>Time:</b> {result["hour"]:02d}:{result["minute"]:02d} UTC (24-hour format)
"""

    if u.channel_post:
        # if previously scheduled, cancel the job
        _addSchedule(u.effective_chat.id, result, chatType="channel")

    elif u.effective_chat.type in "private":
        _addSchedule(u.effective_user.id, result, chatType="private")
    else:
        _addSchedule(chatID, result, chatType="group")

    await message.reply_html(msg)



async def _validateTime(message, text: str):
    """Validate the time format and return the time in 24-hour format."""
    if not text:
        msg = f"""
<b>Please provide a time to schedule the verse.</b>

{validMethod}
"""
        await message.reply_html(msg)
        return False

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
    MessageHandler(filters.Regex(r"^/schedule\s"), scheduleCommand),
]
