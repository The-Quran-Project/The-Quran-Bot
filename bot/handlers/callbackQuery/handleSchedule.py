from telegram.ext import CallbackQueryHandler
from telegram import Update, Bot, InlineKeyboardMarkup


from bot.handlers.database import db


async def handleSchedule(u: Update, c):
    """Handles all the buttons presses / callback queries"""
    bot: Bot = c.bot
    message = u.effective_message
    chatID = u.effective_chat.id

    query = u.callback_query
    queryData = query.data
    method = queryData.split()[1]
    reply = buttons = None

    collection = db.db.schedules
    if method == "delete":
        reply = "Schedule deleted successfully."
        collection.delete_one({"_id": chatID})

    elif method == "enable":
        reply = "Schedule enabled successfully."
        collection.update_one({"_id": chatID}, {"$set": {"enabled": True}})

    elif method == "disable":
        reply = "Schedule disabled successfully."
        collection.update_one({"_id": chatID}, {"$set": {"enabled": False}})

    if not reply:
        return await query.answer("Maybe it was an old message?", show_alert=True)

    # await query.answer()
    await message.edit_text(reply, reply_markup=InlineKeyboardMarkup(buttons or []))
