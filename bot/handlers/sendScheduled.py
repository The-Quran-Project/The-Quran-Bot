import asyncio


from telegram.error import *
from telegram import Bot
from telegram.ext import ContextTypes

from bot.handlers import Quran
from bot.handlers.localDB import db
from datetime import datetime, timezone
from bot.utils import getLogger

logger = getLogger(__name__)


async def jobSendScheduled(context: ContextTypes.DEFAULT_TYPE):
    """Send scheduled verses."""
    bot: Bot = context.bot

    # Statistics tracking
    stats = {"total": 0, "success": 0, "fail": 0, "skipped": 0}

    # Use the scheduleOp method to get all active schedules
    schedules = db.scheduleOp(None, "getActive")
    stats["total"] = len(schedules)
    print()
    for schedule in schedules:
        try:
            chatID = schedule["_id"]
            runTime = schedule["time"]
            hour, minute = runTime.split(":")
            hour, minute = int(hour), int(minute)
            nowHour, nowMinute = datetime.now(timezone.utc).strftime("%H:%M").split(":")
            nowHour, nowMinute = int(nowHour), int(nowMinute)

            # Check if we're within 2 minutes after the scheduled time
            # This prevents multiple sends while allowing for timing flexibility
            time_diff = (nowHour * 60 + nowMinute) - (hour * 60 + minute)

            # Handle day boundary (e.g., scheduled at 23:30, current time 00:30)
            if time_diff < -12 * 60:  # More than 12 hours behind, likely next day
                time_diff += 24 * 60
            elif time_diff > 12 * 60:  # More than 12 hours ahead, likely previous day
                time_diff -= 24 * 60

            if 0 <= time_diff <= 2:
                logger.info(f"Sending scheduled verse to chat {chatID} at {runTime}")

                lastSent = schedule.get("lastSent")
                if lastSent:
                    # Convert lastSent string to timezone-aware datetime
                    lastSent = datetime.strptime(lastSent, "%d:%m:%Y %H:%M:%S")
                    lastSent = lastSent.replace(tzinfo=timezone.utc)
                    diff = datetime.now(timezone.utc) - lastSent
                    # Check if already sent today (within last 23 hours to handle day boundary)
                    if diff.total_seconds() < 23 * 60 * 60:
                        logger.info(f"Skipping chat {chatID} due to recent send")
                        stats["skipped"] += 1
                        continue

                langs = schedule["langs"]
                topicID = schedule.get("topicID")

                # Get random verse
                res = Quran.random()
                verse = res["verse"]
                surahNo = res["surahNo"]
                ayahNo = res["ayahNo"]
                totalAyah = res["totalAyah"]
                surah = Quran.getSurahNameFromNumber(surahNo)

                # Format message
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

                try:
                    await bot.sendMessage(chatID, msg, message_thread_id=topicID)
                    # Update lastSent timestamp
                    db.scheduleOp(chatID, "updateLastSent")
                    stats["success"] += 1

                except ChatMigrated as e:
                    logger.info(f"Chat migrated: {chatID} → {e.new_chat_id}")
                    newChatID = e.new_chat_id
                    # Update chat ID in database
                    db.scheduleOp(chatID, "update", {"_id": newChatID})

                    try:
                        await bot.sendMessage(newChatID, msg, message_thread_id=topicID)
                        db.scheduleOp(newChatID, "updateLastSent")
                        stats["success"] += 1
                    except Exception as e:
                        logger.error(
                            f"Failed to send to migrated chat {newChatID}: {e}"
                        )
                        stats["fail"] += 1

                except Forbidden as e:
                    logger.error(f"Forbidden error for chat {chatID}: {e}")
                    # Disable schedule when bot is removed from chat
                    db.scheduleOp(chatID, "update", {"enabled": False})
                    stats["fail"] += 1

                except Exception as e:
                    logger.error(f"Error sending to chat {chatID}: {e}")
                    stats["fail"] += 1

                # Small delay between sends
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(
                f"Error processing schedule for chat {schedule.get('_id', 'unknown')}: {e}"
            )
            stats["fail"] += 1
            continue

    # Print statistics
    logger.info(
        f"Schedule statistics - Total: {stats['total']}, Success: {stats['success']}, Failed: {stats['fail']}, Skipped: {stats['skipped']}"
    )
    logger.info("Finished checking schedules.")
