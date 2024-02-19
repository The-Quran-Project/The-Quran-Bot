import html

from telegram import Update, Message, Bot, InlineKeyboardButton, InlineKeyboardMarkup

from .database import db


def escapeHtml(text: str):
    return html.escape(str(text))


async def adminCommand(u: Update, c):
    """Sends a message to the user on how to use the bot"""
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)
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
    if not user.get("is_admin"):
        await message.reply_html("<b>You are not an admin</b>")
        return

    reply = """
<u><b>Admin Panel</b></u>

<b>Commands:</b>
/forward <code>chatID</code> [ Reply to a message ]
/getUser <code>chatID</code> [ Reply to a message ]
"""

    await message.reply_html(reply, reply_markup=InlineKeyboardMarkup(buttons))


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




"""About the use of eval:
    As only the developers will be using it, therefore the use of eval is (acceptable)
    
Command:
    /eval expression
"""
async def evaluateCode(u: Update, c):
    """Evaluate an expression and send the output to admin"""
    bot: Bot = c.bot
    message = u.effective_message
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not user.get("is_admin"):
        await message.reply_html("<b>You are not an admin</b>")
        return
    #if not message.reply_to_message:
    #    return await message.reply_html("<b>Reply to an expression</b>")
    
    text = message.text[5:].strip()
    print(text)
    
    try:
        try:
            e2 = None
            output = eval(text)
        except Exception as e2:
            output = await eval(text)
            
        reply = f"""
<b>Output of the expression:</b>
<pre>
{escapeHtml(output)}
</pre>
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
