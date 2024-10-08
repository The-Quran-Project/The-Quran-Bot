import json

from telegram import Update
from telegram.ext import TypeHandler


from .database import db
from .command.updateSettings import updateSettings


async def middleware(u: Update, c):
    """Works as a middleware to add users and chats"""
    if u.inline_query:
        return

    # print(u.to_json())

    if u.channel_post or u.edited_channel_post:
        db.addChannel(u.effective_chat.id)
        return

    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = u.effective_chat.type in ("group", "supergroup")

    user = db.getUser(userID)

    db.updateUser(userID, {"lastMessageTime": u.message.date})
    
    if not user:
        user = db.addUser(userID)
        # If user is new & in private chat, send update settings message
        if not isGroup and u.effective_chat.type == "channel":
            await updateSettings(u, c)

    chat = db.getChat(chatID)

    if isGroup and not chat:  # for groups
        chat = db.addChat(chatID)
