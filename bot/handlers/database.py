import os


from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient


load_dotenv()


if os.environ.get("LOCAL"):
    # For `pymongo.errors.ConfigurationError: cannot open /etc/resolv.conf`
    import dns.resolver

    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class Database:
    def __init__(self) -> None:
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        self.db = self.client.quranbot
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
        self.admins = [i["_id"] for i in self.db.users.find({"is_admin": True})]

    def getAllUsers(self):
        return [i for i in self.db.users.find({})]

    def getAllChat(self):
        return [i for i in self.db.chats.find({})]

    def getAllAdmins(self):
        return [i for i in self.admins]

    def getUser(self, userID: int):
        return self.db.users.find_one({"_id": userID})

    def getChat(self, chatID: int):
        return self.db.chats.find_one({"_id": chatID})

    def addUser(self, userID: int):
        user = {"_id": userID, "settings": self.defaultSettings}
        self.db.users.insert_one(user)
        return user

    def addChat(self, chatID: int):
        chat = {"_id": chatID, "settings": self.defaultGroupSettings}
        self.db.chats.insert_one(chat)
        return chat

    def updateUser(self, userID: int, settings: dict):
        user = self.getUser(userID)
        if not user:
            user = self.addUser(userID)

        settings = {**user["settings"], **settings}

        self.db.users.update_one({"_id": userID}, {"$set": {"settings": settings}})
        return None  # self.getUser(userID)

    def updateChat(self, chatID: int, settings: dict):
        chat = self.getChat(chatID)
        if not chat:
            chat = self.addChat(chatID)

        settings = {**chat["settings"], **settings}

        # TODO : Do it in a better way
        settings["restrictedLangs"] = list(set(settings["restrictedLangs"]))
        self.db.chats.update_one({"_id": chatID}, {"$set": {"settings": settings}})

        return None  # self.getChat(chatID)

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


def main():
    #users = db.getAllUsers()
    chats = db.getAllChat()
    #print("Total Users:", len(users))
    print("Total Chats:", len(chats))
    print(db.getAllAdmins())


if __name__ == "__main__":
    main()
