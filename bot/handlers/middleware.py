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
        db.updateActiveUsers(userID) # add a new active user to the `set`
        user = db.getUser(userID)
        if not user:
            user = db.addUser(userID)
            await updateSettings(u, c)
        else:
            # otherwise, update it. (new user's already have it)
            db.updateUser(userID, {"lastMessageTime": utcTime})

    chat = db.getChat(chatID)

    if isGroup:  # for new groups
        if not chat:
            chat = db.addChat(chatID)
        db.updateChat(chatID, {"lastMessageTime": utcTime})
    
    db.updateCounter() # Update counter for each day
