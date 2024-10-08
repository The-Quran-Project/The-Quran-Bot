import os
import time
import asyncio
import threading
import schedule as scheduleModule

from dotenv import load_dotenv
from collections.abc import Iterable
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient

from .helpers.utils import LimitedStack

load_dotenv()

LOCAL = os.environ.get("LOCAL")

if LOCAL:
    # For `pymongo.errors.ConfigurationError: cannot open /etc/resolv.conf`
    import dns.resolver

    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class _LocalDB:
    """Local Database to store users and chats in memory."""

    def __init__(self, users, chats, channels) -> None:
        self.users = list(users)
        self.chats = list(chats)
        self.channels = list(channels)
        self.admins = [i["_id"] for i in self.users if i.get("is_admin")]
        print(f"LocalDB: {len(self.users)} users, {len(self.chats)} chats")

    def findUser(self, userID: int) -> dict:
        return next((i for i in self.users if i["_id"] == userID), None)

    def findChat(self, chatID: int) -> dict:
        return next((i for i in self.chats if i["_id"] == chatID), None)

    def findChannel(self, channelID: int) -> dict:
        return next((i for i in self.channels if i["_id"] == channelID), None)

    def addUser(self, user) -> None:
        self.users.append(user)
        return None

    def addChat(self, chat) -> None:
        self.chats.append(chat)
        return None

    def addChannel(self, channel) -> None:
        self.channels.append(channel)
        return None

    def updateUser(self, userID: int, settings: dict) -> dict:
        user = self.findUser(userID)
        if not user:
            user = self.addUser(userID)

        user["settings"] = {**user["settings"], **settings}
        return user

    def updateChat(self, chatID: int, settings: dict) -> dict:
        chat = self.findChat(chatID)
        if not chat:
            chat = self.addChat(chatID)

        chat["settings"] = {**chat["settings"], **settings}
        return chat

    def updateChannel(self, channelID: int, settings: dict) -> dict:
        channel = self.findChannel(channelID)
        if not channel:
            channel = self.addChannel(channelID)

        channel["settings"] = {**channel["settings"], **settings}
        return channel

    def getAllUsers(self) -> list:
        return self.users

    def getAllChat(self) -> list:
        return self.chats

    def getAllAdmins(self) -> list:
        return self.admins

    def getAllChannels(self) -> list:
        return self.channels


class Database:
    def __init__(self) -> None:
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        if not LOCAL:
            self.db = self.client.quranbot
        else:
            self.db = self.client.quranbot_local

        self.defaultSettings = {
            "font": 1,  # 1 -> Uthmani, 2 -> Simple
            "showTafsir": True,
            "reciter": 1,  # 1 -> Mishary Rashid Al-Afasy, 2 -> Abu Bakr Al-Shatri
            "primary": "ar",
            "secondary": "en",
            "other": None,
        }
        self.defaultGroupSettings = {
            "handleMessages": False,  # Sending `x:y` for ayah
            "allowAudio": True,  # Allow sending audio recitations
            "previewLink": False,  # Show preview of the Tafsir link
            "restrictedLangs": ["ar"],
        }
        self.defaultChannelSettings = {}

        # --- Local DB ---
        self.queue = []
        channels = self.db.channels.find({})
        chats = self.db.chats.find({})
        users = self.db.users.find({})
        self.localDB = _LocalDB(users, chats, channels)

        # --- Scheduled Tasks ---
        interval = 60
        if os.environ.get("LOCAL"):
            interval = 20

        scheduleModule.every(interval).seconds.do(self.runQueue)

        def runScheduledTasks():
            while True:
                try:
                    scheduleModule.run_pending()
                except Exception as e:
                    print("Error in scheduled tasks:", e)
                time.sleep(1)

        threading.Thread(target=runScheduledTasks).start()

    @property
    def admins(self):
        return self.localDB.getAllAdmins()

    def getAllUsers(self):
        res = self.localDB.getAllUsers()
        return res

    def getAllChat(self):
        res = self.localDB.getAllChat()
        return res

    def getAllChannels(self):
        res = self.localDB.getAllChannels()
        return res

    def getAllAdmins(self):
        res = self.localDB.getAllAdmins()
        return res

    def getUser(self, userID: int):
        res = self.localDB.findUser(userID)
        return res

    def getChat(self, chatID: int):
        res = self.localDB.findChat(chatID)
        return res

    def getChannel(self, channelID: int):
        res = self.localDB.findChannel(channelID)
        return res

    def addUser(self, userID: int):
        user = {"_id": userID, "settings": self.defaultSettings}
        self.localDB.addUser(user)

        func = self.db.users.insert_one
        value = user
        self.queue.append((func, value))
        return user

    def addChat(self, chatID: int):
        chat = {"_id": chatID, "settings": self.defaultGroupSettings}
        self.localDB.addChat(chat)

        func = self.db.chats.insert_one
        value = chat
        self.queue.append((func, value))
        return chat

    def addChannel(self, channelID: int):
        channel = {"_id": channelID, "settings": self.defaultChannelSettings}
        self.localDB.addChannel(channel)

        func = self.db.channels.insert_one
        value = channel
        self.queue.append((func, value))
        return channel

    def updateUser(self, userID: int, settings: dict):
        user = self.getUser(userID)
        settings = {**user["settings"], **settings}
        self.localDB.updateUser(userID, settings)
        func = self.db.users.update_one
        value = ({"_id": userID}, {"$set": {"settings": settings}})
        self.queue.append((func, value))
        return None

    def updateChat(self, chatID: int, settings: dict):
        chat = self.getChat(chatID)
        settings = {**chat["settings"], **settings}
        settings["restrictedLangs"] = list(set(settings["restrictedLangs"]))
        self.localDB.updateChat(chatID, settings)

        func = self.db.chats.update_one
        value = ({"_id": chatID}, {"$set": {"settings": settings}})
        self.queue.append((func, value))
        return None

    def updateChannel(self, channelID: int, settings: dict):
        channel = self.getChannel(channelID)
        settings = {**channel["settings"], **settings}
        self.localDB.updateChannel(channelID, settings)

        func = self.db.channels.update_one
        value = ({"_id": channelID}, {"$set": {"settings": settings}})
        self.queue.append((func, value))
        return None

    def runQueue(self):
        print("--- Running Queue ---\r", end="")
        start = time.time()
        
        for func, value in self.queue:
            if isinstance(value, tuple):
                try:
                    func(*value)
                except Exception as e:
                    print("Error in queue:", e)
            else:
                try:
                    func(value)
                except Exception as e:
                    print("Error in queue:", e)

        end = time.time()
        timeMs = (end - start) * 1000
        self.queue = []
        if timeMs > 100:
            print(f"Time taken: {timeMs:.2f} ms")

    # TODO: keep count of all the requests handled per day
    # Run this in a separate thread or use a TypeHandler to run after the other handlers (group=3)
    # so it doesn't block the event loop
    def updateCounter(self):
        date = time.strftime("%Y-%m-%d")
        self.db.analytics.update_one({"_id": date}, {"$inc": "requests"})

    # def deleteUser(self, userID: int):
    #     return self.db.users.delete_one({"_id": userID})

    # def deleteAllUsers(self):
    #     return self.db.users.delete_many({})

    # def deleteEverything(self):
    #     return
    #     self.db.drop_collection(self.db.users)
    #     self.db.drop_collection(self.db.chats)


db = Database()


async def main():
    db = Database()
    users = db.getAllUsers()
    chats = db.getAllChat()
    print("Total Users:", len(users))
    print("Total Chats:", len(chats))
    print(db.getAllAdmins())


if __name__ == "__main__":
    asyncio.run(main())
