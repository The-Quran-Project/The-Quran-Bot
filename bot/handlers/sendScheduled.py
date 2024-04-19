import time
import asyncio


from telegram.error import *
from telegram import Update, Bot
from telegram.ext import Application, JobQueue, filters, ContextTypes

from . import Quran
from .database import db
from datetime import datetime


async def jobSendScheduled(context: ContextTypes.DEFAULT_TYPE):
    """Send scheduled verses."""
    bot: Bot = context.bot
    collection = db.db.schedules

    print("Checking schedules...")
    schedules = collection.find()
    for schedule in schedules:
        try:
            if not schedule.get("enabled"):
                continue

            chatID = schedule["_id"]
            runTime = schedule["time"]
            hour, minute = runTime.split(":")
            hour, minute = int(hour), int(minute)
            nowHour, nowMinute = datetime.utcnow().strftime("%H:%M").split(":")
            nowHour, nowMinute = int(nowHour), int(nowMinute)
            print(
                f"Chat ID: {chatID}, Time: {runTime}, Now Time: {nowHour}:{nowMinute}"
            )

            if hour == nowHour and abs(nowMinute - minute) <= 10:
                print("Sending scheduled verse...")
                lastSent = schedule.get("lastSent")
                if lastSent:
                    lastSent = datetime.strptime(lastSent, "%d:%m:%Y %H:%M:%S")
                    diff = datetime.utcnow() - lastSent
                    if diff.total_seconds() < 11 * 60:
                        print("Skipping due to last sent.")
                        continue

                langs = schedule["langs"]
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
                    await bot.sendMessage(chatID, msg)
                    collection.update_one(
                        {"_id": chatID}, {"$set": {"lastSent": currentTime}}
                    )
                except ChatMigrated as e:
                    print(f"ChatMigrated: {e}")
                    newChatID = e.new_chat_id
                    collection.update_one({"_id": chatID}, {"$set": {"_id": newChatID}})
                    try:
                        print(f"Sending to new chat ID: {newChatID}")
                        await bot.sendMessage(newChatID, msg)
                        collection.update_one(
                            {"_id": newChatID}, {"$set": {"lastSent": currentTime}}
                        )
                    except Exception as e:
                        print(f"Failing to send to new chat ID: {newChatID} - {e}")

                except Forbidden as e:
                    print(f"Forbidden: {e}")
                    collection.update_one({"_id": chatID}, {"$set": {"enabled": False}})

                except Exception as e:
                    print(f"Error: {e}")

                await asyncio.sleep(0.1)

            # sleep for dueNextMinute seconds
            dueNextMinute = 60 - int(datetime.utcnow().strftime("%S"))
            # await asyncio.sleep(dueNextMinute - 1)
        except Exception as e:
            print(f"Error: {e}")
            continue
    print("Done checking schedules.")
