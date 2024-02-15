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


if os.environ.get("LOCAL"):
    # For `pymongo.errors.ConfigurationError: cannot open /etc/resolv.conf`
    import dns.resolver

    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class Database:
    def __init__(self) -> None:
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        self.db = self.client.quranbot_test  # TODO: Change this to quranbot
        self.defaultSettings = {
            "font": 1,
            "showTafsir": True,
            "reciter": 1,
            "primary": "ar",
            "secondary": "en",
            "other": "bn",
        }

    def getAllUsers(self):
        return [i for i in self.db.users.find({})]

    def getAllChat(self):
        return [i for i in self.db.chats.find({})]

    def getAllAdmins(self):
        return [i for i in self.db.users.find({"is_admin": True})]

    def getUser(self, userID: int):
        return self.db.users.find_one({"_id": userID})

    def getChat(self, chatID: int):
        return self.db.chats.find_one({"_id": chatID})

    def addUser(self, userID: int):
        user = {"_id": userID, "settings": self.defaultSettings}
        self.db.users.insert_one(user)
        return user

    def addChat(self, chatID: int):
        chat = {"_id": chatID}
        self.db.chats.insert_one(chat)
        return chat

    def getChat(self, chatID: int):
        return self.db.chats.find_one({"_id": chatID})

    def updateUser(self, userID: int, settings: dict):
        user = self.getUser(userID)
        if not user:
            user = self.addUser(userID)

        settings = {**user["settings"], **settings}

        self.db.users.update_one({"_id": userID}, {"$set": {"settings": settings}})

        return self.getUser(userID)

    # def deleteUser(self, userID: int):
    #     return self.db.users.delete_one({"_id": userID})

    # def deleteAllUsers(self):
    #     return self.db.users.delete_many({})


db = Database()


def main():
    users = db.getAllUsers()
    chats = db.getAllChat()
    print("Total Users:", len(users))
    print("Total Chats:", len(chats))


if __name__ == "__main__":
    main()
