import json
import traceback

from io import BytesIO
from html import escape
from telegram import Update, Bot, Message
from telegram.ext import CallbackContext

from .database import db


async def handleErrors(u: Update, c: CallbackContext):
    """Handles all the errors raised in the bot"""

    bot: Bot = c.bot

    if not u:
        return

    print("--- Error Occurred ---")
    tbList = traceback.format_exception(None, c.error, c.error.__traceback__)
    tbString = "".join(tbList)

    print(tbString)

    messageSendingError = ""
    try:
        await u.effective_message.reply_html(
            f"""
<b>An error occurred. Report sent to admins</b>

<b>Error:</b>
<code>{escape(str(c.error))}</code>"""
        )
    except Exception as e:
        messageSendingError = str(e)

    caption = f"""
<b><u>#Error{' ❎' if messageSendingError else ''}</u></b>

<b>Chat ID  :</b> <code>{u.effective_chat.id if u.effective_chat else None}</code>
<b>User ID  :</b> <code>{u.effective_user.id}</code>
<b>User     :</b> <a href="tg://user?id={u.effective_user.id}">{escape(u.effective_user.first_name)}</a>
<b>Username : @{u.effective_user.username}</b>
<b>Message ID :</b> <code>{u.effective_message.message_id}</code>
<b>Timestamp  :</b> <code>{u.effective_message.date} UTC</code>
<b>Error:</b>
<blockquote>{escape(c.error)}</blockquote>
"""

    admins = db.getAllAdmins()
    data = {
        "error_message": str(c.error),
        "error": tbString,
        "update": u.to_dict(),
        "sendingError": messageSendingError,
    }
    for admin in admins:
        chatID = admin["_id"]
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
