# from ..quran import QuranClass
# from .database import db

from telegram import Update, Bot
from telegram.ext import CommandHandler


async def scheduleCommand(u:Update, c):
    message = u.effective_message
    chatID = u.effective_chat.id
    userID = u.effective_user.id
    
    