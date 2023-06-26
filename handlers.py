# pylint:disable=W0621
# pylint:disable=W0401
from telegram import *
from telegram.ext import *


import os
import time
import html
import string

from uuid import uuid4
from quran import Quran
from utils import AyahNumberInvalid, SurahNumberInvalid


Quran = Quran()


def esml(x): return html.escape(str(x))


class StaticStickers:
    salam = "CAACAgUAAxkBAAIBEGOtH-MLc6D7antAIRlma1YgnMe7AAJnBAAC3uq4VANpwAelURpaLAQ"
    inShaAllah = "CAACAgUAAxkBAAIBEWOtH-OoB2EaecZw_DAqRwvbHlOZAALWAwACkni4VLa6DL4cB1H6LAQ"
    jazakAllah = "CAACAgUAAxkBAAIBEmOtH-No3_xEGMh2YpM6ErBQ2BHHAAK4AwAC8Yq5VFbQH8fyZNceLAQ"


inMark = InlineKeyboardMarkup
inButton = InlineKeyboardButton

# Adding All Surah Names as Buttons in this list
AllSurah = [[]]


def _divideList(a):
    x = []
    sep = 3
    while a:
        x.append(a[:sep])
        a = a[sep:]
    return x


for i, surah in enumerate(Quran.SURAHS):
    button = inButton(f"{i+1} {surah}", callback_data=f"surah {i+1}")
    length = len(AllSurah[-1])
    totalLen = len(AllSurah)

    if length < 33:
        AllSurah[-1].append(button)
    else:
        nav = [
            inButton("Previous", callback_data=f"prev {totalLen-1}"),
            inButton("Next", callback_data=f"next {totalLen-1}")
        ]
        AllSurah[-1] = _divideList(AllSurah[-1])
        AllSurah[-1].append(nav)

        AllSurah.append([button])

nav = [
    inButton("Previous", callback_data=f"prev {totalLen-1}"),
    inButton("Next", callback_data=f"next {totalLen-1}")
]
AllSurah[-1] = _divideList(AllSurah[-1])
AllSurah[-1].append(nav)


async def start_c(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name
    url = "https://github.com/Nusab19/TG-Quran-Bot"

    say = f"""
Assalamu Alaikum <b>{esml(fn)}!</b>

This bot will give you verses from the Al-Quran.

It can give you the <b>Arabic</b> or <b>English</b> text and also the <b>Audio</b> of each ayah.

This bot is <a href="{url}">open-source</a>. Your contribution can make it more helpful for the Ummah.
    """

    buttons = inMark([
        [inButton("Github", url=url)]
    ])
    x = await bot.sendSticker(chat_id, StaticStickers.salam)
    await bot.sendMessage(chat_id, say, reply_to_message_id=x.message_id, reply_markup=buttons)


async def help_c(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name
    say = f"""
To know how to use the bot:
/use - A brief overview of using the bot.


For any Query, contact @AlQuranDiscussion.

For Updates: @AlQuranUpdates

For contacting directly: @Roboter403 or @Nusab19
    """

    buttons = inMark([
        [inButton("Group", url="https://t.me/AlQuranDiscussion"),
         inButton("Channel", url="https://t.me/AlQuranUpdates")]
    ])

    await bot.sendMessage(chat_id, say, reply_markup=buttons)


async def use_c(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name

    url = "https://telegra.ph/Al-Quran-05-29"

    say = f"""

<u>Basic Commands:</u>
/start - Check if the bot is Alive.
/help - Where to contact the dev and the community.
/info - Details of the current chat.
/ping - Check server's ping.

<u>Usage of Bot:</u>
/surah - The list of all the Surahs

Send any message like:
<code>
surah : ayah </code>
<code>1:3</code>

<b>
Here, `1` means Surah-Fatiha and `3` means ayah 3</b>

For more in depth usage, check the <a href="{url}">Telegraph</a> link.

    """

    buttons = inMark([
        [inButton("Telegraph", url=url)]
    ])

    await bot.sendMessage(chat_id, say, reply_markup=buttons)


async def ping(u, c):
    bot = c.bot
    up = u.effective_message
    mid = up.message_id
    chat_id = u.effective_chat.id
    s = time.time()
    a = await bot.sendMessage(chat_id, "<b>Checking...</b>", reply_to_message_id=mid)

    e = time.time()

    await a.edit_text(f"<b>Took: {(e-s)*1000:.2f} ms</b>")


async def info_c(u, c):
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = esml(u.effective_user.first_name)
    ln = esml(u.effective_user.last_name)
    un = u.effective_user.username

    ulink = f"""
<a href="{f'tg://user?id={user_id}'if not un else f't.me/{un}'}">{fn}</a>
            """.strip()
    un = esml(un)
    date = esml(u.effective_message.date)
    profile_photos = await c.bot.get_user_profile_photos(user_id)

    say = f"""
👆🏻<u><b>Your Profile Photo</b></u> 👌🏻

<b>User ID    :</b> <code>{user_id}</code>
<b>Chat ID    :</b> <code>{chat_id}</code>
<b>First Name :</b> <i>{fn}</i>
<b>Last Name  :</b> <i>{ln}</i>
<b>Username   : @{un}</b>
<b>User Link  :</b> {ulink}
<b>Date       : {date[:-6]}
Time Zone   : +00:00 UTC</b>

<i>To copy your User ID, just tap on it.</i>
    """
    pps = profile_photos["photos"]

    if pps != []:
        one = pps[0][-1]["file_id"]
        await c.bot.sendPhoto(chat_id, one, caption=say)
    else:
        await c.bot.sendMessage(chat_id, say[40:])


async def surah_c(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name
    say = f"""
<b>Select a surah from below:</b>
    """

    # Sends buttons with Surah names
    await bot.sendMessage(chat_id, say, reply_markup=inMark(AllSurah[0]))


def _make_ayah_buttons(surahNo: int or str, ayahNo: int or str):
    button = inMark([[inButton("Prev",
                               callback_data=f"goback {surahNo} {ayahNo}"),
                      inButton("Next",
                               callback_data=f"goforward  {surahNo} {ayahNo}")],
                     [inButton("Change Arabic Style",
                               callback_data=f"change-arabic  {surahNo} {ayahNo}"),
                      inButton("Audio",
                               callback_data=f"audio {surahNo} {ayahNo}")]])

    return button


def _make_ayah_reply(surahNo: int or str, ayahNo: int or str):
    surah = Quran.getSurahNameFromNumber(surahNo)
    ayah = Quran.getAyah(surahNo, ayahNo)
    totalAyah = Quran.getAyahNumberCount(surahNo)

    say = f"""
Surah : {surah} ({surahNo})
Ayah  : <b>{ayahNo} out of {totalAyah}</b>

<u>Arabic</u>
{ayah.arabic}

<u>English</u>
<b>{ayah.english}</b>

<u>Tafsir</u>
<b>Read Here: <a href="{ayah.tafsir}">Telegraph</a></b>
    """
    return say


async def surahCallback(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    chat_id = u.effective_chat.id
    edit_text = up.edit_text

    query = u.callback_query
    query_data = query.data
    # print("Callback Data:", query_data)

    if query_data.startswith("surah"):
        index = int(query_data.split()[1])

        surah = Quran.getSurahNameFromNumber(index)
        ans = f"You selected {surah}"

        # await query.answer(ans)
        say = _make_ayah_reply(index, 1)

        button = _make_ayah_buttons(index, 1)

        await edit_text(say, reply_markup=button)

    elif query_data.startswith(("prev", "next")):
        index = int(query_data.split()[1])
        if query_data.split()[0] == "prev":
            index -= 1
        else:
            index += 1

        if index >= len(AllSurah):
            index = 0

        button = inMark(AllSurah[index])

        await up.edit_reply_markup(button)

    elif query_data.startswith("goback"):
        surahNo, ayahNo = map(int, query_data.split()[1:])

        if surahNo == ayahNo == 1:
            surahNo = 114
            ayahNo = 6

        elif ayahNo == 1:
            surahNo -= 1
            ayahNo = Quran.getAyahNumberCount(surahNo)
        else:
            ayahNo -= 1

        say = _make_ayah_reply(surahNo, ayahNo)

        button = _make_ayah_buttons(surahNo, ayahNo)

        await edit_text(say, reply_markup=button)

    elif query_data.startswith("goforward"):
        surahNo, ayahNo = map(int, query_data.split()[1:])

        if surahNo == 114 and ayahNo == 6:
            surahNo = 1
            ayahNo = 1

        elif ayahNo >= Quran.getAyahNumberCount(surahNo):
            surahNo += 1
            ayahNo = 1
        else:
            ayahNo += 1

        say = _make_ayah_reply(surahNo, ayahNo)

        button = _make_ayah_buttons(surahNo, ayahNo)

        await edit_text(say, reply_markup=button)

    # Toggling the style of Arabic.
    # Toggle between (with and without) harakat
    elif query_data.startswith("change-arabic"):
        surahNo, ayahNo = map(int, query_data.split()[1:])

        surah = Quran.getSurahNameFromNumber(surahNo)
        ayah = Quran.getAyah(surahNo, ayahNo)

        text = up.text_html
        start = text.find("</u>") + 4
        end = text.rfind("<u>English</u>")
        arabic = text[start:end].strip()

        if ayah.arabic == arabic:
            arabic = ayah.arabic2
        else:
            arabic = ayah.arabic

        say = f"""
Surah : {surah} ({surahNo})
Ayah  : {ayahNo}

<u>Arabic</u>
{arabic}

<u>English</u>
<b>{ayah.english}</b>

<u>Tafsir</u>
<b>Read Here: <a href="{ayah.tafsir}">Telegraph</a></b>
        """
        button = _make_ayah_buttons(surahNo, ayahNo)

        await edit_text(say, reply_markup=button)

    elif query_data.startswith("audio"):
        surahNo, ayahNo = map(int, query_data.split()[1:])
        file_id = Quran.getAudioFile(surahNo, ayahNo)

        await bot.sendAudio(chat_id, file_id, reply_to_message_id=up.message_id)
        await query.answer()


async def handleMessage(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name
    text = up.text
    sep = text.split(':')
    button = None

    
    if u.effective_message.via_bot:
        return

    if ':' not in text:
        return await checkSurah(u,c)

    if u.effective_chat != u.effective_user:
        return

    if len(sep) != 2:
        say = """
<b>Your format is not correct.</b>
Give like:

<pre>
surahNo : ayahNo
1:3
</pre>
"""

        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
        return

    surahNo, ayahNo = sep
    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdecimal() and ayahNo.isdecimal()):
        say = """
<b>Surah and Ayah number must be integers</b>
Give like:
<pre>
surahNo : ayahNo
1:3
</pre>
"""

        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
        return

    surahNo = int(surahNo)
    if not 1 <= surahNo <= 114:
        say = """
<b>Surah number needs to be between <i>1</i> to <i>114</i>.</b>
"""

        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
        return

    surah = Quran.getSurahNameFromNumber(surahNo)
    ayahCount = Quran.getAyahNumberCount(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= ayahNo <= ayahCount:
        say = f"""
<b>Surah {surah} has {ayahCount} ayahs only.</b>

But you gave ayah no. {ayahNo}
"""

        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
        return

    say = _make_ayah_reply(surahNo, ayahNo)

    button = _make_ayah_buttons(surahNo, ayahNo)

    await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id, reply_markup=button)


async def checkSurah(u: Update, c):
    bot: Bot = c.bot
    up = u.effective_message
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = u.effective_user.first_name
    text = up.text
    sep = text.split(':')

    if text.isdigit():
        surahNo = int(text)
        if not 1<=surahNo<=114:
            say = """Surah number must be between 1-114"""
            await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
            return

        button = _make_ayah_buttons(surahNo, 1)

        say = _make_ayah_reply(surahNo, 1)
        button = _make_ayah_buttons(surahNo, 1)
        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id, reply_markup=button)
        

    for i in text.lower():
        if i not in string.ascii_lowercase:
            return False

    res: list = Quran.searchSurah(text)
    if not res:
        say = f"""
Couldn't find a Surah matching the text <b>{esml(text)}</b>

Write something like:
fatihah
nas
"""
        await bot.sendMessage(chat_id, say, reply_to_message_id=up.message_id)
        return False

    buttons = []
    for surah, number in res:
        buttons.append(inButton(f"{number} {surah}",
                      callback_data=f"surah {number}"))

    buttons = inMark([buttons])

    await bot.sendMessage(chat_id, "These are the surah that matches the most with the text you sent:", reply_to_message_id=up.message_id, reply_markup=buttons)
    
    return True




# Inline Query Handler

async def handleInlineQuery(u:Update, c):
    query = u.inline_query.query
    inQuery = InlineQueryResultArticle
    if not query:
        return
    
    
    if ':' not in query:
        res = [inQuery(
            id=uuid4(),
            title="Invalid Format",
            input_message_content=InputTextMessageContent("The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"),
            description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
        )
        ]
        await u.inline_query.answer(res)
        return

    sep = query.split(':')
    if len(sep)!=2:
        res = [inQuery(
            id=uuid4(),
            title="Invalid Format",
            input_message_content=InputTextMessageContent("The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"),
            description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
        )
        ]
        await u.inline_query.answer(res)
        return
    
    surahNo, ayahNo = sep
    surahNo = int(surahNo.strip())
    ayahNo = int(ayahNo.strip())
    
    surahName = Quran.getSurahNameFromNumber(surahNo)
    say = _make_ayah_reply(surahNo, ayahNo)
    res=[
        inQuery(
            id=f"{surahNo}:{ayahNo}",
            title=surahName,
            input_message_content=InputTextMessageContent(say),
            description=f"{surahNo}. {surahName} ({ayahNo})",
            thumbnail_url="https://graph.org/file/728d9dda8867352e06707.jpg"
        )
    ]

    await u.inline_query.answer(res)
