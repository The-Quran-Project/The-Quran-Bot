from telegram import Update
import time
import html


def escapeHTML(text: str):
    return html.escape(str(text))


async def pingCommand(u: Update, c):
    """Check the bot's ping"""
    message = u.effective_message
    s = time.time()
    sent = await message.reply_html("<b>Checking...</b>", quote=True)
    e = time.time()

    await sent.edit_text(f"<b>Took: {(e-s)*1000:.2f} ms</b>")


async def infoCommand(u: Update, c):
    """Get info about the user"""
    message = u.effective_message
    userID = u.effective_user.id
    chatID = u.effective_chat.id
    fn = escapeHTML(u.effective_user.first_name)
    ln = escapeHTML(u.effective_user.last_name)
    un = u.effective_user.username
    userLink = f"""<a href="{
        f'tg://user?id={userID}'if not un else f't.me/{un}'}">{fn}</a>""".strip()

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

    if pps != []:
        photo = pps[0][-1]["file_id"]
        await message.reply_photo(
            photo, caption="👆🏻<u><b>Your Profile Photo</b></u> 👌🏻\n\n" + reply
        )
    else:
        await message.reply_html(reply)
