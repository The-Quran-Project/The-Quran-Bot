import json

from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.localDB import db


async def handleAdminButtonPress(u: Update, c):
    """Handles the settings buttons press"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = u.effective_chat.type in ("group", "supergroup")

    user = db.users.get(userID)

    query = u.callback_query
    queryData = query.data

    if not user.get("is_admin"):
        await query.answer("You are not an admin")
        return

    data = queryData.split()

    if data[1] == "users":
        allUsers = db.users.getAll()
        if data[2] == "len":
            await query.answer(f"There are {len(allUsers)} users", show_alert=True)
        elif data[2] == "all":
            await query.answer("Sending all users")
            file = BytesIO(json.dumps(allUsers).encode())
            file.name = "users.json"
            await query.message.reply_document(
                file, caption=f"Total Users: {len(allUsers)}"
            )

    elif data[1] == "chats":
        allChats = db.chats.getAll()
        if data[2] == "len":
            await query.answer(f"There are {len(allChats)} chats", show_alert=True)
        elif data[2] == "all":
            await query.answer("Sending all chats")
            file = BytesIO(json.dumps(allChats).encode())
            file.name = "chats.json"
            await query.message.reply_document(
                file, caption=f"Total Chats: {len(allChats)}"
            )

    elif data[1] == "admins":
        allAdmins = db.getAdmins()
        if data[2] == "len":
            await query.answer(str(len(allAdmins)))
        elif data[2] == "all":
            await query.answer("Sending all admins")
            file = BytesIO(str(allAdmins).encode())
            file.name = "admins.json"
            await query.message.reply_document(
                file, caption=f"Total Admins: {len(allAdmins)}"
            )

    elif data[1] == "active":
        activeUsers = db.getActiveUsers()
        if data[2] == "len":
            await query.answer(str(len(activeUsers)))
        elif data[2] == "all":
            await query.answer("Sending all active users")
            file = BytesIO(str(activeUsers).encode())
            file.name = "activeUsers.json"
            await query.message.reply_document(
                file, caption=f"Total Active Users: {len(activeUsers)}"
            )
