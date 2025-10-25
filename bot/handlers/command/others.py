import html
import json
import time
from telegram import Update
from telegram.ext import CommandHandler
from datetime import datetime
from bot.handlers.helpers.decorators import onlyGroupAdmin


currentTimeUTC = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")

async def getVersion(u: Update, c):
    """Check the bot's version that's running"""

    message = u.effective_message
    await message.reply_html(f"<b>Version:</b> <code>{currentTimeUTC}</code>")



def escapeHTML(text: str):
    return html.escape(str(text))


async def pingCommand(u: Update, c):
    """Check the bot's ping"""

    message = u.effective_message
    s = time.time()
    msg = await message.reply_html("<b>Checking...</b>")
    e = time.time()

    await msg.edit_text(f"<b>Took: {(e-s)*1000:.2f} ms</b>")


async def infoCommand(u: Update, c):
    """Get info about the user"""

    message = u.effective_message
    text = message.text.split()[-1]
    if text.lower() == "json":
        return await message.reply_html(f"<pre>{escapeHTML(u.to_json())}</pre>")

    if message.reply_to_message:
        user = message.reply_to_message.from_user

    else:
        user = message.from_user

    chatID = u.effective_chat.id
    userID = user.id
    fn = escapeHTML(user.first_name)
    ln = escapeHTML(user.last_name)
    un = user.username
    userLink = f"""<a href="{f'tg://user?id={userID}'if not un else f't.me/{un}'}">{fn}</a>""".strip()
    un = escapeHTML(un)
    date = escapeHTML(u.effective_message.date.strftime("%d-%m-%Y %H:%M:%S"))
    profile_photos = await c.bot.get_user_profile_photos(userID)

    reply = f"""
<b>User ID    :</b> <code>{userID}</code>
<b>Chat ID    :</b> <code>{chatID}</code>
<b>First Name :</b> <i>{fn}</i>
<b>Last Name  :</b> <i>{ln}</i>
<b>Username   : @{un}</b>
<b>User Link  :</b> {userLink}
<b>Date       : {date}
Time Zone   : +00:00 UTC</b>

<i>To copy your User ID, just tap on it.</i>
"""

    pps = profile_photos["photos"]

    if pps and u.effective_chat.type == "private":
        photo = pps[0][-1]["file_id"]
        await message.reply_photo(
            photo, caption=f"👆🏻<u><b>Your Profile Photo</b></u> 👌🏻\n\n{reply}"
        )

    else:
        await message.reply_html(reply)


@onlyGroupAdmin(allowDev=True)
async def showJson(u: Update, c):
    """Show the json of the update"""

    message = u.effective_message
    reply = f"""
<pre>
{json.dumps(u.to_dict(), indent=2)}
</pre>
"""

    await message.reply_html(reply)


exportedHandlers = [
    CommandHandler("ping", pingCommand),
    CommandHandler("info", infoCommand),
    CommandHandler("showJson", showJson),
    CommandHandler("version", getVersion),
]
