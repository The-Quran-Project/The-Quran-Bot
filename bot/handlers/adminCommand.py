from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from .database import db

buttons = [
    [
        InlineKeyboardButton("Users Len", callback_data="admin users len"),
        InlineKeyboardButton("Get Users", callback_data="admin users all"),
    ],
    [
        InlineKeyboardButton("Chats Len", callback_data="admin chats len"),
        InlineKeyboardButton("Get Chats", callback_data="admin chats all"),
    ],
    [
        InlineKeyboardButton("Admins Len", callback_data="admin admins len"),
        InlineKeyboardButton("Get Admins", callback_data="admin admins all"),
    ],
]


async def adminCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not user.get("is_admin"):
        await message.reply_html("<b>You are not an admin</b>")
        return

    reply = "<b>Admin Panel</b>"
    button = InlineKeyboardMarkup(buttons)

    await message.reply_html(reply, reply_markup=button, quote=True)

# 5596148289, 1046846204
