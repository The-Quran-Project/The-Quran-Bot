import re
import time
from typing import List, Optional, Tuple, Dict, Any

from bot.handlers.localDB import db
from bot.handlers import Quran
from bot.handlers.helpers.decorators import onlyGroupAdmin

from datetime import datetime, timezone
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes


def _addScheduleToTemp(
    chatID: int,
    time: str,
    chatType: str,
    langs: List[str],
    topicID: Optional[int] = None,
) -> Dict[str, Any]:
    """Add a schedule to the database.

    Args:
        chatID: The chat ID to add the schedule for
        time: The time in 24-hour format (HH:MM)
        chatType: The type of chat (private, group, channel)
        langs: List of language codes to use for the schedule
        topicID: Optional topic ID for forum threads

    Returns:
        The created schedule document
    """
    # Ensure we have at least one language and limit to 3
    langs = [i for i in langs if i] or ["english_1"]
    langs = langs[:3]

    data = {
        "time": time,
        "chatType": chatType,
        "langs": langs,
        "enabled": True,
    }
    if topicID:
        data["topicID"] = topicID

    # Use the scheduleOp method to add the schedule
    return db.scheduleOp(chatID, "add", data)


validMethod = """\
<b><u>Examples:</u></b>
<code>/schedule 11:49 pm</code>
<code>/schedule 11:49 am</code>
<code>/schedule 23:49</code> (24-hour format)
<code>/schedule 11:49 pm - ara eng urd</code> (Multiple languages)

<b><i>Note:</i></b>
Spaces don't matter. You can put languages at the end with a hyphen.
<code>11 : 49 pm</code> is the same as <code>11:49pm</code>"""


# Regex pattern to match time formats with optional languages
pattern = re.compile(
    r"^(?P<hour>\d{1,2})\s*:\s*(?P<minute>\d{1,2})\s*(?P<ampm>[ap]\s*m)?\s*(-\s*(?P<langs>[a-z]{3}(?:\s+[a-z]{3})*))?$",
    re.IGNORECASE,
)


@onlyGroupAdmin(allowDev=True)
async def scheduleCommand(u: Update, c: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /schedule command to create or view schedules.

    Format: /schedule [time] - [languages]
    Examples:
        /schedule - View current schedule
        /schedule 11:49 pm - eng ara
    """
    message = u.effective_message
    chatID = u.effective_chat.id

    # Parse command arguments
    splitted = " ".join(message.text.split()[1:]).lower().split("-")
    text = splitted[0].strip()
    langs = splitted[1].split() if len(splitted) > 1 else []

    # If no time provided, show current schedule
    if not text:
        return await showSchedule(u, c)

    # Validate time format
    result = await _validateTime(message, text)
    if not result:
        return

    # Process language codes
    langs = [Quran.detectLanguage(i) for i in langs]
    langs = list(dict.fromkeys(langs))  # Remove duplicates
    languages = [str(Quran.getTitleLanguageFromLang(i)) for i in langs]

    # Calculate time remaining
    currentTime = datetime.now(timezone.utc)
    hours, minutes = result.split(":")
    scheduled_time = datetime(
        year=currentTime.year,
        month=currentTime.month,
        day=currentTime.day,
        hour=int(hours),
        minute=int(minutes),
        second=0,
        tzinfo=timezone.utc,
    )

    # Handle case when scheduled time is earlier than current time
    if scheduled_time < currentTime:
        scheduled_time = scheduled_time.replace(day=scheduled_time.day + 1)

    remaining = scheduled_time - currentTime
    remaining_str = time.strftime("%H:%M:%S", time.gmtime(remaining.total_seconds()))

    # Prepare confirmation message
    msg = f"""
<b>Schedule Enabled</b>
A random verse will be sent at the following time:

<b>Time:</b> {result} UTC (24-hour format)
<b>Remaining:</b> {remaining_str}

<b>Language:</b> {', '.join(languages) or "English"}

{any(lang is None for lang in languages) and "<i>Invalid language(s) will be ignored.</i>" or ""}
"""
    buttons = [
        [
            InlineKeyboardButton("Delete", callback_data="schedule delete"),
            InlineKeyboardButton("Disable", callback_data="schedule disable"),
        ],
        [
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ]

    # Add schedule based on chat type
    if u.channel_post:
        _addScheduleToTemp(chatID, result, chatType="channel", langs=langs)
    elif u.effective_chat.type == "private":
        _addScheduleToTemp(chatID, result, chatType="private", langs=langs)
    else:
        topicID = message.message_thread_id
        _addScheduleToTemp(
            chatID, result, chatType="group", langs=langs, topicID=topicID
        )

    await message.reply_html(msg, reply_markup=InlineKeyboardMarkup(buttons))


async def showSchedule(u: Update, c: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current schedule for a chat."""
    message = u.effective_message
    chatID = u.effective_chat.id

    # Get schedule from database
    data = db.scheduleOp(chatID, "get")
    if not data:
        return await message.reply_html(
            "No schedule found. See /use for more information."
        )

    # Extract schedule details
    runTime = data.get("time")
    langs = data.get("langs", [])
    chatType = data.get("chatType", "unknown")
    enabled = data.get("enabled", False)

    # Format language names
    languages = [str(Quran.getTitleLanguageFromLang(i)) for i in langs]
    hours, minutes = runTime.split(":")

    # Calculate time remaining
    currentTime = datetime.now(timezone.utc)
    scheduled_time = datetime(
        year=currentTime.year,
        month=currentTime.month,
        day=currentTime.day,
        hour=int(hours),
        minute=int(minutes),
        second=0,
        tzinfo=timezone.utc,
    )

    # Handle case when scheduled time is earlier than current time
    if scheduled_time < currentTime:
        scheduled_time = scheduled_time.replace(day=scheduled_time.day + 1)

    remaining = scheduled_time - currentTime
    remaining_str = time.strftime("%H:%M:%S", time.gmtime(remaining.total_seconds()))

    # Prepare schedule information message
    msg = f"""
<b>Schedule Information</b>
A random verse will be sent at the following time:

<b>Time:</b> {hours}:{minutes} UTC (24-hour format)
<b>Remaining:</b> {remaining_str}

<b>Languages:</b> <code>{', '.join(languages) or "English"}</code>
<b>Status:</b> <i>{"Enabled" if enabled else "Disabled"}</i>
<b>Chat ID:</b> <code>{chatID}</code>
<b>Chat Type:</b> {chatType.capitalize()}
"""
    buttons = [
        [
            (
                InlineKeyboardButton("Disable", callback_data="schedule disable")
                if enabled
                else InlineKeyboardButton("Enable", callback_data="schedule enable")
            ),
        ],
        [
            InlineKeyboardButton("Delete", callback_data="schedule delete"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
    ]

    await message.reply_html(msg, reply_markup=InlineKeyboardMarkup(buttons))


async def _validateTime(message, text):
    """Validate the time format and convert to 24-hour format.

    Args:
        message: The message object
        text: The time text to validate

    Returns:
        The validated time in 24-hour format (HH:MM) or None if invalid
    """
    # Remove spaces and lowercase
    text = text.replace(" ", "").lower()

    # Try to match the pattern
    match = pattern.match(text)
    if not match:
        await message.reply_html(validMethod)
        return None

    # Extract components
    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    ampm = match.group("ampm")

    # Validate hour and minute
    if minute > 59:
        await message.reply_html("❌ <b>Invalid minute</b>. Must be between 0-59.")
        return None

    # Convert to 24-hour format if needed
    if ampm:
        if hour > 12:
            await message.reply_html(
                "❌ <b>Invalid hour</b>. For AM/PM format, hour must be between 1-12."
            )
            return None

        if hour == 12:
            hour = 0

        if "p" in ampm:
            hour += 12
    elif hour > 23:
        await message.reply_html(
            "❌ <b>Invalid hour</b>. For 24-hour format, hour must be between 0-23."
        )
        return None

    # Format as HH:MM
    return f"{hour:02d}:{minute:02d}"


# Export handlers for the module
exportedHandlers = [
    CommandHandler("schedule", scheduleCommand),
    MessageHandler(
        filters.ChatType.CHANNEL & filters.Regex(r"^/schedule"), scheduleCommand
    ),
]
