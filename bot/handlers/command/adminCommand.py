import html

from telegram.ext import CommandHandler, filters
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ..database import db
from ..replies import adminCommands
from ..helpers.decorators import onlyDeveloper


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
    if chatID[1:].isdigit():  # ignore the '-' if it's a group
        try:
            await message.reply_to_message.forward(chatID)
            await message.reply_html("<b>Message forwarded</b>")
        except Exception as e:
            await message.reply_html(f"<b>Error:</b> <code>{e}</code>")

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


@onlyDeveloper(notifyNonAdminUsers=False)
async def deleteMessage(u: Update, c):
    """Deletes a message"""
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not message.reply_to_message:
        # await message.reply_html("<b>Reply to a message</b>")
        return

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        pass


@onlyDeveloper()
async def getUser(u: Update, c):
    """Gets a user's details"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    chatID = message.text.split()[1]
    if not chatID[1:].isdigit():
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
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    text = message.text[5:].strip()
    print(text)

    e2 = None
    try:
        try:
            output = await eval(text)
            print(output)
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


exportedHandlers = [
    CommandHandler("admin", adminCommand, filters.User(db.getAllAdmins())),
    CommandHandler("forward", forwardMessage, filters.User(db.getAllAdmins())),
    CommandHandler("getUser", getUser, filters.User(db.getAllAdmins())),
    CommandHandler("eval", evaluateCode, filters.User(db.getAllAdmins())),
]
