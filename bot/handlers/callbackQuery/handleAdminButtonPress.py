import json

from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.database import db


async def handleAdminButtonPress(u: Update, c):
    """Handles the settings buttons press"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = u.effective_chat.type in ("group", "supergroup")

    user = db.getUser(userID)

    query = u.callback_query
    queryData = query.data

    if not user.get("is_admin"):
        await query.answer("You are not an admin")
        return

    data = queryData.split()

    if data[1] == "users":
        if data[2] == "len":
            await query.answer(
                f"There are {len(db.getAllUsers())} users", show_alert=True
            )
        elif data[2] == "all":
            await query.answer("Sending all users")
            # send a json file of all users. don't save the file in local disk
            # save it in buffer and send it
            allUsers = db.getAllUsers()
            file = BytesIO(json.dumps(allUsers).encode())
            file.name = "users.json"
            await query.message.reply_document(
                file, caption=f"Total Users: {len(allUsers)}"
            )

    elif data[1] == "chats":
        if data[2] == "len":
            await query.answer(
                f"There are {len(db.getAllChat())} chats", show_alert=True
            )
        elif data[2] == "all":
            await query.answer("Sending all chats")
            allChats = db.getAllChat()
            file = BytesIO(json.dumps(allChats).encode())
            file.name = "chats.json"
            await query.message.reply_document(
                file, caption=f"Total Chats: {len(allChats)}"
            )

    elif data[1] == "admins":
        if data[2] == "len":
            await query.answer(str(len(db.getAllAdmins())))
        elif data[2] == "all":
            await query.answer("Sending all admins")
            allAdmins = db.getAllAdmins()
            file = BytesIO(str(allAdmins).encode())
            file.name = "admins.json"
            await query.message.reply_document(
                file, caption=f"Total Admins: {len(allAdmins)}"
            )

    # elif data[1] == "broadcast":
    #     await query.answer("Sending broadcast message")
    #     await query.message.reply_text("Enter the message to broadcast")
    #     await c.wait_for("message")
    #     await query.message.reply_text("Broadcasting message")
    #     await query.message.reply_text("Message sent to all users")
