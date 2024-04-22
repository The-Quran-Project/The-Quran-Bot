from functools import wraps
from typing import Callable

from telegram import Update, Message, Bot

from ..database import db

developers = db.admins


def onlyDeveloper(func: Callable):
    @wraps(func)
    async def wrapper(u: Update, c, *a, **k):
        if u.channel_post:
            return await func(u, c, *a, **k)

        if u.effective_user.id not in developers:
            return await u.effective_message.reply_html(
                "<b>You are not authorized to use this command</b>"
            )
        return await func(u, c, *a, **k)

    return wrapper


def onlyGroupAdmin(func: Callable):
    @wraps(func)
    async def wrapper(u: Update, c, *a, **k):
        if u.effective_chat.type not in ("group", "supergroup"):
            return await func(u, c, *a, **k)

        chatID = u.effective_chat.id
        userID = u.effective_user.id

        if userID == 1087968824:  # Group Anonymous Bot
            return await func(u, c, *a, **k)

        admins = [i.user.id for i in await u.effective_chat.get_administrators()]
        if userID not in admins:
            return await u.effective_message.reply_html(
                "<b>You must be an admin of the group to use this command</b>"
            )
        return await func(u, c, *a, **k)

    return wrapper
