from pymongo import MongoClient, UpdateOne, DeleteOne
from dotenv import load_dotenv
from collections import deque
from bot.utils import getLogger
from bot.handlers.defaults import (
    defaultChannelSettings,
    defaultGroupSettings,
    defaultSettings,
)
import threading
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from bot.utils.log import getLogger

load_dotenv()
LOCAL = os.environ.get("LOCAL")

logger = getLogger(__name__)


class CachedCollection:
    """
    A simple caching wrapper around a MongoDB collection.

    Stores data in-memory for fast access and queues writes
    to MongoDB, which are flushed in bulk for efficiency.

    Attributes:
        collection: The PyMongo collection instance.
        cache: A dictionary acting as the in-memory cache.
        queue: A queue (deque) holding update operations.

    Example:
        >>> client = MongoClient("mongodb+srv://<user>:<pass>@cluster.mongodb.net")
        >>> db = client["quranbot"]
        >>> users = CachedCollection(db["users"])
        >>> users.set(1234, {"_id": 1234, "name": "Ali"})
        >>> print(users.get(1234))
        >>> users.flush()  # Push all queued writes to MongoDB
    """

    def __init__(self, mongo_collection):
        self.collection = mongo_collection
        self.cache = {}
        self.queue = deque()
        self._load_initial_cache()

    def _load_initial_cache(self) -> None:
        """Load all documents from MongoDB into the in-memory cache."""
        for doc in self.collection.find():
            self.cache[doc["_id"]] = doc

        self.start_auto_flush()

    def get(self, _id) -> Optional[Dict[str, Dict | Any]]:
        """
        Retrieve a document from the cache.

        Args:
            _id (any): Document ID.

        Returns:
            dict or None: Cached document if it exists.
        """
        return self.cache.get(_id)

    def getAll(self) -> List[Dict[str, Any]]:
        """
        Retrieve all documents from the cache.

        Returns:
            list: List of cached documents.
        """
        return list(self.cache.values())

    def set(self, _id, data) -> Dict[str, Any]:
        """
        Add or update a document in the cache and queue the update.

        Args:
            _id (any): Document ID.
            data (dict): Document data to cache and persist.

        Returns:
            dict: The updated document that was cached.

        Example:
            >>> users.set(1234, {"_id": 1234, "name": "Ali"})
        """
        data["_id"] = _id
        if not self.cache.get(_id):
            self.cache[_id] = {}

        self.cache[_id].update(data)

        self.queue.append(UpdateOne({"_id": _id}, {"$set": data}, upsert=True))
        return data

    def delete(self, _id) -> bool:
        """
        Delete a document from the cache and queue the deletion.

        Args:
            _id (any): Document ID to delete.

        Returns:
            bool: True if document was found and deleted, False otherwise.

        Example:
            >>> users.delete(1234)
        """
        if _id in self.cache:
            del self.cache[_id]
            self.queue.append(DeleteOne({"_id": _id}))
            return True
        return False

    def updateSettings(self, _id, data) -> Dict[str, Any]:
        """
        Update a document's settings in the cache and queue the update.

        Args:
            _id (any): Document ID.
            data (dict): Settings data to update and persist.

        Returns:
            dict: The updated document that was cached.

        Example:
            >>> users.updateSettings(1234, {"language": "ar"})
        """
        if _id not in self.cache:
            self.set(_id, data)
            return data

        self.cache[_id]["settings"].update(data)
        self.queue.append(
            UpdateOne(
                {"_id": _id},
                {"$set": {"settings": self.cache[_id]["settings"]}},
                upsert=True,
            )
        )
        return self.cache[_id]

    def flush(self) -> bool:
        """
        Flush all queued writes to MongoDB using bulk_write.

        Returns:
            bool: True if flush was successful, False otherwise.

        Example:
            >>> users.flush()
        """
        if not self.queue:
            return True

        queue_size = len(self.queue)
        start_time = time.time()

        try:
            self.collection.bulk_write(list(self.queue))
            elapsed_time = time.time() - start_time
            logger.info(
                f"Successfully processed {queue_size} updates in {elapsed_time:.2f} seconds"
            )
            self.queue.clear()
            return True

        except Exception as e:
            logger.error(f"Error during bulk write operation: {str(e)}")
            # Don't clear queue on error so updates can be retried
            return False

    def start_auto_flush(self, interval=60) -> threading.Thread:
        """
        Start a background thread to flush updates to MongoDB periodically.

        Args:
            interval (int): Time in seconds between flushes.

        Returns:
            threading.Thread: The started background thread.

        Example:
            >>> users.start_auto_flush(interval=30)
        """

        def loop():
            while True:
                try:
                    self.flush()
                except Exception as e:
                    logger.error(f"Auto-flush error: {e}")
                time.sleep(interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        return thread


class Database:
    def __init__(self, db_name: str) -> None:
        uri = os.environ.get("MONGODB_URI")
        db_name = db_name if not LOCAL else "quranbot-dev"
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users = CachedCollection(self.db["users"])
        self.chats = CachedCollection(self.db["chats"])
        self.channels = CachedCollection(self.db["channels"])
        self.analytics = CachedCollection(self.db["analytics"])
        self.schedules = CachedCollection(self.db["schedules"])

    def addChannel(self, channelID) -> Dict[str, Any]:
        """Add a new channel with default channel settings

        Args:
            channelID: The ID of the channel to add

        Returns:
            dict: The newly created channel document
        """
        return self.channels.set(channelID, {"settings": defaultChannelSettings})

    def addChat(self, chatID) -> Dict[str, Any]:
        """Add a new chat with default group settings

        Args:
            chatID: The ID of the chat to add

        Returns:
            dict: The newly created chat document
        """
        return self.chats.set(chatID, {"settings": defaultGroupSettings})

    def addUser(self, userID) -> Dict[str, Any]:
        """Add a new user with default settings

        Args:
            userID: The ID of the user to add

        Returns:
            dict: The newly created user document
        """
        return self.users.set(userID, {"settings": defaultSettings})

    def getActiveUsers(self) -> List[int]:
        """Get a list of active users based on lastMessageTime

        Returns:
            list: A list of active user documents
        """
        active = []
        for user in self.users.getAll():
            if user.get("lastMessageTime"):
                active.append(user.get("_id"))

        return active

    def getAdmins(self) -> List[int]:
        """Get a list of admin users based on is_admin flag

        Returns:
            list: A list of admin user documents
        """
        admins = []
        for user in self.users.getAll():
            if user.get("is_admin"):
                admins.append(user.get("_id"))

        return admins

    def scheduleOp(
        self,
        chatID: Optional[int],
        operation: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Consolidated method for schedule operations.

        Args:
            chatID: The chat ID for the schedule. None for operations that don't require a specific chat ID.
            operation: The operation to perform (get, getAll, getActive, add, update, toggle, updateLastSent, delete).
            data: Additional data for the operation (optional).

        Returns:
            The result of the operation, which depends on the operation type.
        """
        if operation == "get":
            return self.schedules.get(chatID)

        elif operation == "getAll":
            return list(self.schedules.cache.values())

        elif operation == "getActive":
            return [s for s in self.schedules.cache.values() if s.get("enabled", False)]

        elif operation == "add":
            if not data:
                return None
            return self.schedules.set(chatID, data)

        elif operation == "update":
            if not data:
                return None
            schedule = self.schedules.get(chatID)
            if schedule:
                schedule.update(data)
                return self.schedules.set(chatID, schedule)
            return None

        elif operation == "toggle":
            schedule = self.schedules.get(chatID)
            if schedule:
                schedule["enabled"] = not schedule.get("enabled", False)
                return self.schedules.set(chatID, schedule)
            return None

        elif operation == "updateLastSent":
            schedule = self.schedules.get(chatID)
            if schedule:
                schedule["lastSent"] = datetime.now().strftime("%d:%m:%Y %H:%M:%S")
                return self.schedules.set(chatID, schedule)
            return None

        elif operation == "delete":
            return self.schedules.delete(chatID)

        return None

    # # thread version
    # def updateCounter(self) -> None:
    #     """Update the daily request counter in the analytics collection.

    #     Creates a new document for each day with the date as _id and
    #     increments the requests counter. Runs in a separate thread to
    #     avoid blocking the main thread.

    #     Returns:
    #         None
    #     """
    #     date = time.strftime("%Y-%m-%d")
    #     func = lambda: self.db.analytics.update_one(
    #         {"_id": date}, {"$inc": {"requests": 1}}, upsert=True
    #     )
    #     threading.Thread(target=func).start()

    # queue version
    def updateCounter(self) -> None:
        """
        Update the daily request counter in the analytics collection.

        Adds the update operation to the queue to be flushed with other operations.
        Creates a document for each day with the date as _id and increments the requests counter.

        Returns:
            None
        """
        date = time.strftime("%Y-%m-%d")

        # Get current count or default to 0
        analytics_doc = self.analytics.get(date) or {"_id": date, "requests": 0}
        analytics_doc["requests"] += 1

        # Add to queue using the existing mechanism
        self.analytics.set(date, analytics_doc)


db = Database("quranbot")

# --- Example Usage ---
if __name__ == "__main__":
    # Replace with your MongoDB Atlas URI
    password = "0092100921"
    MONGO_URI = f"mongodb+srv://Nusab19:{password}@firstcluster.eh81nbz.mongodb.net/?retryWrites=true&w=majority&appName=FirstCluster"
    client = MongoClient(MONGO_URI)
    dbtest = client["quranbot"]
    logger.info(client.list_database_names())

    users = CachedCollection(dbtest["users"])
    users.set(212, {"name": "Ali", "language": "en"})
    logger.info(f"User 1: {users.get(1)}")

    users.set(222, {"name": "Fatima", "language": "ar"})
    logger.info(f"User 2: {users.get(2)}")

    logger.info(users.get(1))
    logger.info(users.get(212))
    logger.info(users.get(222))

    # users.flush()  # Optional, or use start_auto_flush() for automatic background flush

    # Optional: background flush every 30 seconds
    # users.start_auto_flush(30)

    logger.info("Done.")
