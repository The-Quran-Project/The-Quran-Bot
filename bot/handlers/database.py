import os
import time
import asyncio
import schedule
import threading

from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient


load_dotenv()


if os.environ.get("LOCAL"):
    # For `pymongo.errors.ConfigurationError: cannot open /etc/resolv.conf`
    import dns.resolver

    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class LocalDB:
    """Local Database to store users and chats in memory."""

    def __init__(self, users: list, chats: list) -> None:
        self.users = list(users)
        self.chats = list(chats)
        self.admins = [i["_id"] for i in self.users if i.get("admin")]
        print(f"LocalDB: {len(self.users)} users, {len(self.chats)} chats")

    def findUser(self, userID: int) -> dict:
        return next((i for i in self.users if i["_id"] == userID), None)

    def findChat(self, chatID: int) -> dict:
        return next((i for i in self.chats if i["_id"] == chatID), None)

    def addUser(self, user) -> None:
        self.users.append(user)
        return None

    def addChat(self, chat) -> None:
        self.chats.append(chat)
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

    def getAllUsers(self) -> list:
        return self.users

    def getAllChat(self) -> list:
        return self.chats

    def getAllAdmins(self) -> list:
        return self.admins


class Database:
    def __init__(self) -> None:
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        self.db = self.client.development
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
        # --- Local DB ---
        self.queue = []
        users = self.db.users.find({})
        chats = self.db.chats.find({})
        self.localDB = LocalDB(users, chats)

        # --- Scheduled Tasks ---
        schedule.every(20).seconds.do(self.runQueue)

        def runScheduledTasks():
            while True:
                try:
                    schedule.run_pending()
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

    def getAllAdmins(self):
        res = self.localDB.getAllAdmins()
        return res

    def getUser(self, userID: int):
        res = self.localDB.findUser(userID)
        return res

    def getChat(self, chatID: int):
        res = self.localDB.findChat(chatID)
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

    def updateUser(self, userID: int, settings: dict):
        user = self.getUser(userID)
        if not user:
            user = self.addUser(userID)

        settings = {**user["settings"], **settings}
        self.localDB.updateUser(userID, settings)
        func = self.db.users.update_one
        value = ({"_id": userID}, {"$set": {"settings": settings}})
        self.queue.append((func, value))
        return None

    def updateChat(self, chatID: int, settings: dict):
        chat = self.getChat(chatID)
        if not chat:
            chat = self.addChat(chatID)

        settings = {**chat["settings"], **settings}
        settings["restrictedLangs"] = list(set(settings["restrictedLangs"]))
        self.localDB.updateChat(chatID, settings)

        func = self.db.chats.update_one
        value = ({"_id": chatID}, {"$set": {"settings": settings}})
        self.queue.append((func, value))
        return None

    def runQueue(self):
        print("--- Running Queue ---")
        start = time.time()

        for func, value in self.queue:
            if isinstance(value, tuple):
                func(*value)
            else:
                func(value)

        end = time.time()
        self.queue = []
        print(f"Time taken: {end - start:.2f}s")

    # TODO: keep count of all the requests handled per day
    # Run this in a separate thread or use a TypeHandler to run after the other handlers (group=3)
    # so it doesn't block the event loop
    def updateCounter(self, date: str):
        self.db.update_one({"_id": date}, {"$inc": "requests"})

    # def deleteUser(self, userID: int):
    #     return self.db.users.delete_one({"_id": userID})

    # def deleteAllUsers(self):
    #     return self.db.users.delete_many({})

    def deleteEverything(self):
        return
        self.db.drop_collection(self.db.users)
        self.db.drop_collection(self.db.chats)


db = Database()


async def main():
    users = db.getAllUsers()
    chats = db.getAllChat()
    print("Total Users:", len(users))
    print("Total Chats:", len(chats))
    print(db.getAllAdmins())


if __name__ == "__main__":
    asyncio.run(main())
