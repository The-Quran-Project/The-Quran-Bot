import html
import json
import traceback

from io import BytesIO
from .database import db
from telegram.ext import CallbackContext
from telegram import Update, Bot, Message


def escape(text: any):
    return html.escape(str(text))


async def handleErrors(u: Update | None, c: CallbackContext):
    """Handles all the errors raised in the bot"""

    bot: Bot = c.bot
    errorString = str(c.error)
    if "terminated" in errorString:
        return

    if not u:
        data = {"error": errorString, "update": str(c.update), "context": str(c)}
        text = "<b>#Error</b>\n\nNo Update Error"
        return await bot.sendDocument(
            5596148289,
            BytesIO(json.dumps(data, indent=4, ensure_ascii=False).encode()),
            filename="error-unknown.json",
            caption=text,
        )

    message = u.effective_message
    user = u.effective_user
    chat = u.effective_chat

    print("--- Error Occurred ---")
    tbList = traceback.format_exception(None, c.error, c.error.__traceback__)
    tbString = "".join(tbList)

    # check if the error has telegram.error.BadRequest: User not found error
    # if "User not found" in errorString:
    #        return await u.effective_message.reply_html(
    #            "<b>Couldn't check if you are an Admin or not due to Telegram side error</b>. \n<code>telegram.error.BadRequest: User not found</code>\nContact @Roboter403 if this error persists."
    #        )

    messageSendingError = ""
    if "Message is not modified" in errorString:
        return print(f"Error: {c.error}")

    print(tbString)
    try:
        await message.reply_html(
            f"""
<b>An error occurred. Report sent to admins</b>

<b>Error:</b>
<code>{escape(errorString)}</code>"""
        )
    except Exception as e:
        messageSendingError = str(e)

    caption = f"""
<b><u>#Error</u>{' ❎' if messageSendingError else ''}</b>

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

    data = {
        "error_message": errorString,
        "error": tbString.replace("\\n", "\n"),
        "update": u.to_dict(),
        "sendingError": messageSendingError,
    }

    admins = db.getAllAdmins()
    chatID = 5596148289
    if not u.effective_chat:
        return await bot.sendDocument(
            chatID,
            BytesIO(json.dumps(data, indent=4, ensure_ascii=False).encode()),
            filename=f"error-{user.id if user else 12345}.json",
            caption=caption,
            reply_to_message_id=msgID,
        )

    try:
        msgID = None
        er = "None"
        try:
            msgID: Message = (
                await bot.forwardMessage(
                    chatID, chat.id if chat else user.id, message.message_id
                )
            ).message_id
        except Exception as er:
            er = str(er)
            data["reportError"] = er

        await bot.sendDocument(
            chatID,
            BytesIO(json.dumps(data, indent=4, ensure_ascii=False).encode()),
            filename=f"error-{user.id if user else 12345}.json",
            caption=caption,
            reply_to_message_id=msgID,
        )
    except Exception as e:
        print(f"Error while sending error report to {admin}: {e}")
