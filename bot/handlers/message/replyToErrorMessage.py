import html

from telegram import Update, Bot
from telegram.ext import CallbackContext


def escape(text: any) -> str:
    return html.escape(str(text))


async def replyToErrorMessage(u: Update, c: CallbackContext):
    """Reply to the user with the error message"""
    bot: Bot = c.bot
    message = u.effective_message
    repliedTo = u.effective_message.reply_to_message

    if (
        not repliedTo
        or not message.text  # if replied with something else
        or not repliedTo.document  # if doesn't have the json file
        or not repliedTo.document.file_name.startswith("error-")
    ):
        return False

    # `filename` = error-<userID>.json
    # - you thought about regex?
    # - Nope! Not happening ❄
    userID = repliedTo.document.file_name[6:-5]
    htmlText = message.text_html

    reply = f"""
<b>Message from the Developer:</b>

{htmlText}
"""
    options = {
        "$userName": repliedTo.from_user.username,
        "$userID": repliedTo.from_user.id,
        "$chatID": repliedTo.chat.id,
        "$chatName": repliedTo.chat.title,
        "$firstName": repliedTo.from_user.first_name,
        "$lastName": repliedTo.from_user.last_name,
    }
    for key, value in options.items():
        reply = reply.replace(key, escape(value))

    try:
        await bot.sendMessage(userID, reply)
        await message.reply_html("<b>Sent the message to the user</b>")
    except Exception as e:
        await message.reply_html(
            f"Error sending message:\n<code>{html.escape(str(e))}</code>"
        )

    return True
