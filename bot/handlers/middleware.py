from telegram import Update

from .database import db
from .helpers import updateSettings


async def middleware(u: Update, c):
    """Works as a middleware to add/ban users and chats"""
    if u.inline_query:
        return

    userID = u.effective_user.id
    chatID = u.effective_chat.id
    isGroup = chatID != userID

    user = db.getUser(userID)
    chat = db.getChat(chatID)

    if not user:
        user = db.addUser(userID)
        # If user is new, send update settings message
        await updateSettings(u, c)

    if isGroup and not chat:  # for groups
        chat = db.addChat(chatID)

    if user["banned"]:
        # TODO: ban user
        pass

    if isGroup and chat["banned"]:
        pass
    message_thread_id = u.effective_message.message_thread_id

    if message_thread_id:
        bot.sendMessage(chat_id=chatID, text="Your message", message_thread_id=message_thread_id)
    else:
        bot.sendMessage(chat_id=chatID, text="Your message")
