import html
import json
import traceback

from io import BytesIO
from bot.handlers.database import db
from telegram.ext import CallbackContext
from telegram import Update, Bot, Message
from bot.utils import getLogger


logger = getLogger(__name__)

def escape(text: any):
    return html.escape(str(text))


predefinedErrors = {
    "Not enough rights to send text messages to the chat": """
It seems like I don't have enough rights to send messages in <b>"$GROUPNAME"</b>. Tell the admins to give me the permission to send messages in the chat.

<b>How to fix:</b>
1. Make sure that the bot is not restricted/muted in the chat.
2. Bot has proper permissions to send messages in the chat.

This message is sent to you because the bot doesn't have enough rights to send messages in that chat.
""",
    "Message can't be deleted for everyone": """
It seems like I don't have enough rights to delete messages in this chat. Tell the admins to give me the permission to delete messages in this chat.

Otherwise, you can delete the message manually.
""",
    "Not enough rights to send music to the chat": """
I don't have enough rights to send the audio file in the chat. Tell the admins to give me the permission to send audio files in this chat.
""",
}


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

    logger.info("--- Error Occurred ---")
    tbList = traceback.format_exception(None, c.error, c.error.__traceback__)
    tbString = "".join(tbList)

    # check if the error has telegram.error.BadRequest: User not found error
    # if "User not found" in errorString:
    #        return await u.effective_message.reply_html(
    #            "<b>Couldn't check if you are an Admin or not due to Telegram side error</b>. \n<code>telegram.error.BadRequest: User not found</code>\nContact @Roboter403 if this error persists."
    #        )

    messageSendingError = ""
    if "Message is not modified" in errorString:
        logger.error(f"Error: {c.error}")
        return

    if predefinedErrors.get(errorString):
        reply = predefinedErrors[errorString].replace("$GROUPNAME", escape(chat.title))
        await message.reply_html(reply)
        return

    print(tbString)

    try:
        if "flood control" in errorString.lower():
            raise Exception("Self Flood Controlled")

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

Reply to this message to send a message to the user. (Only Text) [Supports Formatting]
"""

    data = {
        "error_message": errorString,
        "error": tbString,
        "update": u.to_dict(),
        "sendingError": messageSendingError,
    }

    # chatID = 5596148289
    chatID = -1002245250917  # Error Reporting Group
    msgID = None

    if not u.effective_chat:
        await bot.sendDocument(
            chatID,
            BytesIO(json.dumps(data, indent=4, ensure_ascii=False).encode()),
            filename=f"error-{user.id if user else 12345}.json",
            caption=caption,
        )
        return None

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
