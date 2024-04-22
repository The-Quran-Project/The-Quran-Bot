from functools import wraps
from typing import Callable

from telegram import Update, Message, Bot

from ..database import db

developers = db.admins


def onlyDeveloper(notifyNonAdminUsers: bool = True):
    """
    Decorator to check if the user is a developer

    Parameters:
        notifyNonAdminUsers (bool): Whether to notify non-admin users that they are not authorized to use the command

    Returns:
        wrapper (Callable): The wrapper function
    """

    def outerWrapper(func: Callable):
        @wraps(func)
        async def wrapper(u: Update, c, *a, **k):
            if u.channel_post:
                return await func(u, c, *a, **k)

            if u.effective_user.id not in developers:
                if not notifyNonAdminUsers:
                    return
                return await u.effective_message.reply_html(
                    "<b>You are not authorized to use this command</b>"
                )
            return await func(u, c, *a, **k)

        return wrapper

    return outerWrapper


def onlyGroupAdmin(allowDev: bool = False, notifyNonAdminUsers: bool = True):
    """
    Decorator to check if the user is an admin of the group

    Parameters:
        allowDev (bool): Whether to allow developers to use the command
        notifyNonAdminUsers (bool): Whether to notify non-admin users that they are not authorized to use the command

    Returns:
        wrapper (Callable): The wrapper function
    """

    def outerWrapper(func: Callable):
        @wraps(func)
        async def wrapper(u: Update, c, *a, **k):
            if allowDev and u.effective_user.id in developers:
                return await func(u, c, *a, **k)

            if u.effective_chat.type not in ("group", "supergroup"):
                return await func(u, c, *a, **k)

            userID = u.effective_user.id

            if userID == 1087968824:  # Group Anonymous Bot
                return await func(u, c, *a, **k)

            admins = [i.user.id for i in await u.effective_chat.get_administrators()]
            if userID not in admins:
                if not notifyNonAdminUsers:
                    return
                return await u.effective_message.reply_html(
                    "<b>You must be an admin of the group to use this command</b>"
                )
            return await func(u, c, *a, **k)

        return wrapper

    return outerWrapper
