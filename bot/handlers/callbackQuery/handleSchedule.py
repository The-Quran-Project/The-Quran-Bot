from typing import Optional, Tuple, List

from telegram import Update, Bot, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.handlers.localDB import db
from bot.utils import getLogger

logger = getLogger(__name__)


async def handleSchedule(u: Update, c: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle schedule-related callback queries.

    Supported actions:
    - delete: Remove the schedule
    - enable: Enable the schedule
    - disable: Disable the schedule
    """
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    query = u.callback_query
    queryData = query.data
    method = queryData.split()[1]
    reply = None
    buttons = None

    try:
        if method == "delete":
            reply = "Schedule deleted successfully."
            success = db.scheduleOp(chatID, "delete")
            if not success:
                reply = "No schedule found to delete."

        elif method == "enable":
            reply = "Schedule enabled successfully."
            result = db.scheduleOp(chatID, "update", {"enabled": True})
            if not result:
                reply = "Failed to enable schedule. Schedule not found."

        elif method == "disable":
            reply = "Schedule disabled successfully."
            result = db.scheduleOp(chatID, "update", {"enabled": False})
            if not result:
                reply = "Failed to disable schedule. Schedule not found."

        else:
            # Unknown method
            return await query.answer("Unknown schedule operation.", show_alert=True)

        if not reply:
            return await query.answer(
                "Operation failed. Maybe it was an old message?", show_alert=True
            )

        # Acknowledge the callback query
        await query.answer()

        # Update the message with the result
        await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons or []))

    except Exception as e:
        logger.error(f"Error handling schedule callback for chat {chatID}: {e}")
        await query.answer(
            "An error occurred while processing your request.", show_alert=True
        )
