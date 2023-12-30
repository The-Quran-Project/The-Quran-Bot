from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputTextMessageContent,
    InlineQueryResultArticle,
)

from uuid import uuid4

from . import Quran
from .helpers import getAyahReply
from .database import db


async def handleInlineQuery(u: Update, c):
    """Handles the inline query"""
    query = u.inline_query.query
    inQuery = InlineQueryResultArticle
    userID = u.effective_user.id
    user = db.getUser(userID)

    if not user:
        db.addUser(userID)

    if not query:
        return

    if ":" not in query:
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>",
            )
        ]
        await u.inline_query.answer(res)
        return

    sep = query.split(":")
    if "" in sep:
        sep.remove("")

    if len(sep) < 2:
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>",
            )
        ]
        await u.inline_query.answer(res)
        return

    surahNo, ayahNo, *ext = sep

    surahNo = surahNo.strip()
    ayahNo = ayahNo.strip()

    if not (surahNo.isdigit() and ayahNo.isdigit()):
        res = [
            inQuery(
                id=uuid4(),
                title="Invalid Format",
                input_message_content=InputTextMessageContent(
                    "The format is not correct. Give like: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="SurahNo and AyahNo must be numbers.",
            )
        ]
        await u.inline_query.answer(res)
        return

    surahNo = int(surahNo)
    ayahNo = int(ayahNo)

    if not 1 <= surahNo <= 144:
        res = [
            inQuery(
                id=uuid4(),
                title="Surah Not Valid",
                input_message_content=InputTextMessageContent(
                    "Surah Number must be between 1 114\nFormat: <code>surahNo : ayahNo</code> <code>1:3</code>"
                ),
                description="Surah Number not Valid",
            )
        ]
        await u.inline_query.answer(res)
        return

    ayahCount = Quran.getAyahNumberCount(surahNo)

    if not 1 <= ayahNo <= ayahCount:
        res = [
            inQuery(
                id=uuid4(),
                title="Ayah Not Valid",
                input_message_content=InputTextMessageContent(
                    f"Surah {Quran.getSurahNameFromNumber(surahNo)} has {ayahCount} ayahs only."
                ),
                description=f"Surah {Quran.getSurahNameFromNumber(surahNo)} has {ayahCount} ayahs only.",
            )
        ]
        await u.inline_query.answer(res)
        return

    surahName = Quran.getSurahNameFromNumber(surahNo)
    reply = getAyahReply(userID, surahNo, ayahNo)
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Try Inline Query",
                    switch_inline_query_current_chat=f"{surahNo}:{ayahNo}",
                )
            ]
        ]
    )
    res = [
        inQuery(
            id=uuid4(),
            title=surahName,
            input_message_content=InputTextMessageContent(
                reply, disable_web_page_preview=True
            ),
            description=f"{surahNo}. {surahName} ({ayahNo})",
            thumbnail_url="https://graph.org/file/728d9dda8867352e06707.jpg",
            reply_markup=buttons,
        )
    ]

    await u.inline_query.answer(res, cache_time=1)
