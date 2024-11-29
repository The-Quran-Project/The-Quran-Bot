import os
import html
import asyncio
import hashlib


from datetime import datetime, timezone

from telegram.ext import CommandHandler, filters
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from bot.handlers.database import db
from bot.handlers.replies import adminCommands
from bot.handlers.helpers.decorators import onlyDeveloper
from bot.utils import getLogger

logger = getLogger(__name__)


def escapeHtml(text: str):
    return html.escape(str(text))


@onlyDeveloper()
async def adminCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
    message = u.effective_message
    userID = u.effective_user.id
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
        [
            InlineKeyboardButton("Active Users Len", callback_data="admin active len"),
            InlineKeyboardButton("Get Active Users", callback_data="admin active all"),
        ],
    ]
    reply = f"""
<u><b>Admin Panel</b></u>

{adminCommands}
"""

    await message.reply_html(reply, reply_markup=InlineKeyboardMarkup(buttons))


@onlyDeveloper()
async def forwardMessage(u: Update, c):
    """Forwards a message to a chat or All chats"""
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not message.reply_to_message:
        await message.reply_html("<b>Reply to a message</b>")
        return

    chatID = message.text.split()[1]
    if chatID[1:].isdecimal():  # ignore the '-' if it's a group
        try:
            await message.reply_to_message.forward(chatID)
            await message.reply_html("<b>Message forwarded</b>")
        except Exception as e:
            await message.reply_html(f"<b>Error:</b> <code>{e}</code>")

        return

    if chatID == "me":
        try:
            await message.reply_to_message.forward(userID)
            await message.reply_html("<b>Message forwarded</b>")
        except Exception as e:
            await message.reply_html(f"<b>Error:</b> <code>{e}</code>")

        return

    reply = """
Sending message to <b>{total}</b> users.

Success: {success}
Failed: {failed}

Progress: {progress}%
"""

    if chatID == "all":
        users = db.getActiveUsers()  # send message to the active users only
        success = 0
        errors = 0
        m = await message.reply_text(
            reply.format(total=len(users), success=success, failed=errors, progress=0)
        )
        if not users:
            return await m.edit_text("No user to forward to!")

        with open("success.txt", "w") as f, open("errors.txt", "w") as g:
            f.write("")
            g.write("")

        for count, userID in enumerate(users, 1):
            try:
                await message.reply_to_message.forward(userID)
                success += 1
                with open("success.txt", "a") as f:
                    f.write(f"{userID}\n")

            except Exception as e:
                logger.error(f"Error while forwarding to {userID}: {e}")
                errors += 1
                with open("errors.txt", "a") as f:
                    f.write(f"{userID} - {e}\n")
            finally:
                await asyncio.sleep(0.3)

            # edit the message after 10 iterations
            currentTime = datetime.now(timezone.utc).strftime(
                "%d %B %Y, %H:%M:%S %A UTC"
            )
            if count % 10 == 0:
                text = (
                    reply.format(
                        total=len(users),
                        success=success,
                        failed=errors,
                        progress=round(count / len(users), 2),
                    )
                    + "\n"
                    + currentTime
                )
                try:
                    await m.edit_text(text)
                except Exception as e:
                    logger.error(f"Error editing the message in forward: {e}")

        # after the loop is finished
        await m.reply_html("<b>Message forwarded to all users</b>")
        await m.reply_document(
            open("success.txt", "rb"),
            caption=f"<b>Success</b>\nCount: <code>{success} / {len(users)}</code>",
        )
        await m.reply_document(
            open("errors.txt", "rb"),
            caption=f"<b>Errors</b>\nCount: <code>{errors} / {len(users)}</code>",
        )
        return

    await message.reply_html("<b>Invalid chatID</b>")


async def loginAsAdmin(u: Update, c):
    """Login as admin"""
    message = u.effective_message
    chatType = u.effective_chat.type
    userID = u.effective_user.id
    hashedPass = "b0cc3016f19b4ac2aece3b1312a213b91bfd93224c50615e0952034aa2baf300b3a41e31de8f7e629dc9c23f79a8aadb43eb41e69cfc96dccf99ce83538055dc"

    if chatType != "private":
        return await message.reply_text("<b>Try in private chat!</b>")

    text = message.text.split()[-1]  # yeah, it's just one word
    if hashlib.sha512(text.encode("utf8")).hexdigest() != hashedPass:
        return await message.reply_text("<b>Wrong password. Sorry :p</b>")

    db.localDB.admins.append(userID)
    await message.reply_text(f"<b>Successfully logged in with {userID = }</b>")


@onlyDeveloper(notifyNonAdminUsers=False)
async def deleteMessage(u: Update, c):
    """Deletes a message"""
    message = u.effective_message
    chatType = u.effective_chat.type

    if not message.reply_to_message:
        if chatType == "private":
            await message.reply_html("<b>Reply to a message</b>")
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        if chatType == "private":
            logger.error(f"Error while deleting message: {e}")
            raise e


@onlyDeveloper()
async def getUser(u: Update, c):
    """Gets a user's details"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    chatID = message.text.split()[1]
    if not chatID[1:].isdecimal():
        await message.reply_html("<b>Invalid chatID</b>")
        return

    user = chat = await bot.getChat(chatID)

    if chatID[0] == "-":
        perms = chat.permissions.to_dict()

        permText = "\n".join(
            f"<b>{i.replace('_',' ').title()}:</b> {'✅' if j else '❌'}"
            for (i, j) in perms.items()
        )

        reply = f"""
ID: <code>{chat.id}</code>
Type: <b>{chat.type.capitalize()}</b>
Title: <b>{chat.title}</b>
Username: <b>@{chat.username}</b>
Description:
<b>{escapeHtml(chat.description)}</b>

<u><b>Permissions:</b></u>
{permText}
"""

    else:
        reply = f"""
ID: <code>{user.id}</code>
Type: <b>{user.type.capitalize()}</b>
First Name: <b>{user.first_name}</b>
Last Name: <b>{user.last_name}</b>
Username: <b>@{user.username}</b>
Bio:
<b>{escapeHtml(user.bio)}</b>
"""
    await message.reply_html(reply)


# Command:
#     /eval expression
@onlyDeveloper()
async def evaluateCode(u: Update, c):
    """Evaluate an expression and send the output to admin"""
    import os, sys, httpx, json, telegram, logging, asyncio, io, math, base64, hashlib, datetime, time

    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id

    text = message.text[5:].strip()
    if "help" in text:
        return  # TODO: Fix
    e2 = None
    try:
        try:
            output = await eval(text)
            logger.info(output)
        except Exception as e:
            output = eval(text)
            e2 = str(e)

        reply = f"""
<b>Output of the expression:</b>

<pre>
{escapeHtml(output)}
</pre>

<b>Error 2:</b> <code>{e2}</code>
"""

    except Exception as e:
        reply = f"""
<b>Error while evaluating the expression:</b>

<pre>
{escapeHtml(e)}
</pre>

<b>Error 2:</b> <code>{e2}</code>
"""

    await message.reply_html(reply)


@onlyDeveloper()
async def raiseError(u: Update, c):
    """Gets a user's details"""
    bot: Bot = c.bot
    message = u.effective_message
    await message.reply_html("<b>Raising...</b>")
    raise IndexError("Meow")


exportedHandlers = [
    CommandHandler("admin", adminCommand),
    CommandHandler("forward", forwardMessage),
    CommandHandler("getUser", getUser),
    CommandHandler("eval", evaluateCode),
    CommandHandler("login", loginAsAdmin),
    CommandHandler("delete", deleteMessage),
    CommandHandler("error", raiseError),
]
