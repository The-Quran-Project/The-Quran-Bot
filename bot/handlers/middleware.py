from telegram import Update

from .database import db
from .helpers import updateSettings


async def middleware(u: Update, c):
    """Works as a middleware to add users and chats"""
    if u.inline_query:
        return

    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = chatID != userID

    user = db.getUser(userID)
    
    if not user:
        user = db.addUser(userID)
        # If user is new & in private chat, send update settings message
        if not isGroup:
            await updateSettings(u, c)

    chat = db.getChat(chatID)

    if isGroup and not chat:  # for groups
        chat = db.addChat(chatID)
