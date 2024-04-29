import html
import json
import traceback

from io import BytesIO
from .database import db
from telegram.ext import CallbackContext
from telegram import Update, Bot, Message


def escape(text: any):
    return html.escape(str(text))


async def handleErrors(u: Update, c: CallbackContext):
    """Handles all the errors raised in the bot"""

    bot: Bot = c.bot

    if not u:
        return

    print("--- Error Occurred ---")
    tbList = traceback.format_exception(None, c.error, c.error.__traceback__)
    tbString = "".join(tbList)

    # check if the error has telegram.error.BadRequest: User not found error
    if "User not found" in str(c.error):
        return await u.effective_message.reply_html(
            "<b>Couldn't check if you are an Admin or not due to Telegram side error</b>. \n<code>telegram.error.BadRequest: User not found</code>\nContact @Roboter403 if this error persists."
        )

    messageSendingError = ""
    if "Message is not modified" in str(c.error):
        return print(f"Error: {c.error}")

    print(tbString)
    try:
        await u.effective_message.reply_html(
            f"""
<b>An error occurred. Report sent to admins</b>

<b>Error:</b>
<code>{escape(str(c.error))}</code>"""
        )
    except Exception as e:
        messageSendingError = str(e)
    
    user = u.effective_user
    chat = u.effective_chat
    message = u.effective_message
    caption = f"""
<b><u>#Error{' ❎' if messageSendingError else ''}</u></b>

<b>Type     :</b> {chat.type if chat else None}
<b>Chat ID  :</b> <code>{chat.id if chat else None}</code>
<b>User ID  :</b> <code>{user.id if user else None}</code>
<b>User     :</b> <a href="tg://user?id={user.id if user else 123}">{escape(user.first_name if user else None)}</a>
<b>Username : @{user.username if user else None}</b>
<b>Message ID :</b> <code>{message.message_id}</code>
<b>Timestamp  :</b> <code>{message.date} UTC</code>
<b>Error:</b>
<blockquote>{escape(c.error)}</blockquote>
"""

    admins = db.getAllAdmins()
    data = {
        "error_message": str(c.error),
        "error": tbString.replace("\\n", "\n"),
        "update": u.to_dict(),
        "sendingError": messageSendingError,
    }
    for admin in admins:
        chatID = admin
        try:
            # forward the message the user sent
            msgID = None
            if u.effective_chat:
                msgID: Message = (
                    await bot.forwardMessage(
                        chatID,
                        u.effective_chat.id,
                        u.effective_message.message_id,
                    )
                ).message_id

            await bot.sendDocument(
                chatID,
                BytesIO(json.dumps(data, indent=4, ensure_ascii=False).encode()),
                filename=f"error-{u.effective_user.id}.json",
                caption=caption,
                reply_to_message_id=msgID,
            )
        except Exception as e:
            print(f"Error while sending error report to {admin}: {e}")

        return  # Send error to one admin only 
