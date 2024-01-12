from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

import os


load_dotenv()

# base structure
{
    "_id": 1,
    "settings": {
        "ayahMode": 1,  # 1 -> Full Ayah, 2 -> Only Arabic, 3 -> Only Translation
        "arabicStyle": 1,  # 1 -> Uthmani, 2 -> Simple
        "showTafsir": True,
    },
    "banned": False,
}


class Database:
    def __init__(self) -> None:
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        self.db = self.client.quranbot
        self.defaultSettings = {
            "ayahMode": 1,
            "arabicStyle": 1,
            "showTafsir": True,
        }

    def getAllUsers(self):
        return [i for i in self.db.users.find({})]

    def getAllChat(self):
        return [i for i in self.db.chats.find({})]

    def getUser(self, chatID: str or int):
        return self.db.users.find_one({"_id": chatID})

    def getChat(self, chatID: str or int):
        return self.db.chats.find_one({"_id": chatID})

    def addUser(self, chatID: str or int):
        user = {
            "_id": chatID,
            "settings": self.defaultSettings,
            "banned": False,
        }
        self.db.users.insert_one(user)
        return user

    def addChat(self, chatID: str or int):
        chat = {
            "_id": chatID,
            "banned": False,
        }
        self.db.chats.insert_one(chat)
        return chat

    def getChat(self, chatID: str or int):
        return self.db.chats.find_one({"_id": chatID})

    def updateUser(self, chatID: str or int, settings: dict):
        user = self.getUser(chatID)
        if not user:
            user = self.addUser(chatID)

        settings = {**user["settings"], **settings}
        self.db.users.update_one({"_id": chatID}, {"$set": {"settings": settings}})
        return self.getUser(chatID)

    def banUser(self, userID: str or int):
        return self.db.users.update_one({"_id": userID}, {"$set": {"banned": True}})

    def unBanUser(self, userID: str or int):
        return self.db.users.update_one({"_id": userID}, {"$set": {"banned": False}})

    def banChat(self, chatID: str or int):
        return self.db.chats.update_one({"_id": chatID}, {"$set": {"banned": True}})

    def unBanChat(self, chatID: str or int):
        return self.db.chats.update_one({"_id": chatID}, {"$set": {"banned": False}})

    def deleteUser(self, chatID: str or int):
        return self.db.users.delete_one({"_id": chatID})

    def deleteAllUsers(self):
        return self.db.users.delete_many({})


db = Database()


def main():
    print("Total Users:", len(db.getAllUsers()))
    print("Total Chats:", len(db.getAllChat()))
    print(db.updateUser(1, {"ayahMode": 3}))
    print(db.getUser(1))


if __name__ == "__main__":
    main()
