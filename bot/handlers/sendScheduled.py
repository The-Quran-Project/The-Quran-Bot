import asyncio


from telegram.error import *
from telegram import Bot
from telegram.ext import ContextTypes

from bot.handlers import Quran
from bot.handlers.database import db
from datetime import datetime, timezone
from bot.utils import getLogger

logger = getLogger(__name__)


async def jobSendScheduled(context: ContextTypes.DEFAULT_TYPE):
    """Send scheduled verses."""
    bot: Bot = context.bot
    collection = db.db.schedules

    schedules = collection.find()
    logger.dump(schedules)
    print(schedules)

    for schedule in schedules:
        try:
            if not schedule.get("enabled"):
                continue

            chatID = schedule["_id"]
            runTime = schedule["time"]
            hour, minute = runTime.split(":")
            hour, minute = int(hour), int(minute)
            nowHour, nowMinute = datetime.now(timezone.utc).strftime("%H:%M").split(":")
            nowHour, nowMinute = int(nowHour), int(nowMinute)

            if hour == nowHour and (0 <= nowMinute - minute <= 5):
                logger.info("Sending scheduled verse...")
                logger.info(
                    f"Chat ID: {chatID}, Time: {runTime}, Now Time: {nowHour}:{nowMinute}"
                )
                lastSent = schedule.get("lastSent")
                if lastSent:
                    lastSent = datetime.strptime(lastSent, "%d:%m:%Y %H:%M:%S")
                    diff = datetime.now(timezone.utc) - lastSent
                    if diff.total_seconds() < 11 * 60:
                        logger.info("Skipping due to last sent.")
                        continue

                langs = schedule["langs"]
                topicID = schedule.get("topicID")
                res = Quran.random()
                verse = res["verse"]
                surahNo = res["surahNo"]
                ayahNo = res["ayahNo"]
                totalAyah = res["totalAyah"]
                surah = Quran.getSurahNameFromNumber(surahNo)
                msg = f"""
<b>Random Scheduled Verse</b>
Surah : <b>{surah} ({surahNo})</b>
Ayah  : <b>{ayahNo} out of {totalAyah}</b>
    """
                for lang in langs:
                    title = Quran.getTitleLanguageFromLang(lang)
                    ayah = verse[lang]
                    msg += f"""
<u><b>{title}</b></u>
<blockquote>{ayah}</blockquote>
    """
                currentTime = datetime.now().strftime("%d:%m:%Y %H:%M:%S")
                try:
                    await bot.sendMessage(chatID, msg, message_thread_id=topicID)
                    collection.update_one(
                        {"_id": chatID}, {"$set": {"lastSent": currentTime}}
                    )
                except ChatMigrated as e:
                    logger.info(f"ChatMigrated: {e}")
                    newChatID = e.new_chat_id
                    collection.update_one({"_id": chatID}, {"$set": {"_id": newChatID}})
                    try:
                        logger.info(f"Sending to new chat ID: {newChatID}")
                        await bot.sendMessage(newChatID, msg, message_thread_id=topicID)
                        collection.update_one(
                            {"_id": newChatID}, {"$set": {"lastSent": currentTime}}
                        )
                    except Exception as e:
                        logger.error(
                            f"Failing to send to new chat ID: {newChatID} - {e}"
                        )

                except Forbidden as e:
                    logger.error(f"Forbidden: {e}")
                    collection.update_one({"_id": chatID}, {"$set": {"enabled": False}})

                except Exception as e:
                    logger.error(f"Error: {e}")

                await asyncio.sleep(0.1)

            # sleep for dueNextMinute seconds
            dueNextMinute = 60 - int(datetime.now(timezone.utc).strftime("%S"))
            # await asyncio.sleep(dueNextMinute - 1)
        except Exception as e:
            logger.error(f"Error: {e}")
            continue
    logger.info("Done checking schedules.")
