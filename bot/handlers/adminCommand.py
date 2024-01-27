from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup

import html

from .database import db


def escapeHtml(text: str):
    return html.escape(str(text))


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

    reply = """
<u><b>Admin Panel</b></u>

<b>Commands:</b>
/forward <code>chatID</code> [ Reply to a message ]
/get <code>chatID</code> [ Reply to a message ]
"""
    button = InlineKeyboardMarkup(buttons)

    await message.reply_html(reply, reply_markup=button, quote=True)


async def forwardMessage(u: Update, c):
    """Forwards a message to a chat or All chats"""
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not user.get("is_admin"):
        await message.reply_html("<b>You are not an admin</b>")
        return

    if not message.reply_to_message:
        await message.reply_html("<b>Reply to a message</b>")
        return

    chatID = message.text.split()[1]
    if chatID.isdigit():
        try:
            await message.reply_to_message.forward(chatID)
            await message.reply_html("<b>Message forwarded</b>")
        except Exception as e:
            await message.reply_html(f"<b>Error:</b> <code>{e}</code>", quote=True)

        return

    if chatID == "all":
        users = db.getAllUsers()
        success = 0
        errors = 0
        for user in users:
            userID = user["_id"]
            try:
                await message.reply_to_message.forward(userID)
                with open("success.txt", "a") as f:
                    f.write(f"{userID}\n")

                success += 1

            except Exception as e:
                print(f"Error while forwarding to {userID}: {e}")
                with open("errors.txt", "a") as f:
                    f.write(f"{userID}\n")

                errors += 1

        await message.reply_html("<b>Message forwarded to all users</b>")

        await message.reply_document(
            open("success.txt", "rb"),
            caption=f"<b>Success</b>\nCount: <code>{success} / {len(users)}</code>",
        )
        await message.reply_document(
            open("errors.txt", "rb"),
            caption=f"<b>Errors</b>\nCount: <code>{errors} / {len(users)}</code>",
        )
        return

    await message.reply_html("<b>Invalid chatID</b>")


async def getUser(u: Update, c):
    """Gets a user's details"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not user.get("is_admin"):
        await message.reply_html("<b>You are not an admin</b>")
        return

    chatID = message.text.split()[1]
    if not chatID.isdigit():
        await message.reply_html("<b>Invalid chatID</b>")
        return

    user = await bot.getChat(chatID)

    reply = f"""
First Name: <b>{user.first_name}</b>
Last Name: <b>{user.last_name}</b>
Username: <b>@{user.username}</b>
ID: <code>{user.id}</code>
"""
    await message.reply_html(reply, quote=True)
