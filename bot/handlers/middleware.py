from datetime import datetime, timezone

from telegram import Update

from bot.handlers.database import db
from bot.handlers.command.updateSettings import updateSettings


async def middleware(u: Update, c):
    """Works as a middleware to add users and chats"""
    if u.inline_query:
        return

    # print(u.to_json())

    if u.channel_post or u.edited_channel_post:
        db.addChannel(u.effective_chat.id)
        return

    utcTime = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    chatType = u.effective_chat.type
    isGroup = chatType in ("group", "supergroup")

    # Only check for a new user in the private chat
    if userID == chatID:
        user = db.getUser(userID)
        if not user:
            user = db.addUser(userID)
            # If user is new & in private chat, send update settings message
            if not isGroup and chatType == "channel":
                await updateSettings(u, c)
        db.updateUser(userID, {"lastMessageTime": utcTime})

    chat = db.getChat(chatID)

    if isGroup and not chat:  # for groups
        chat = db.addChat(chatID)
