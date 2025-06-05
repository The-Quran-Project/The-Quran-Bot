from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
from collections import deque
from bot.utils import getLogger
import threading
import time
import os

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

    def _load_initial_cache(self):
        """Load all documents from MongoDB into the in-memory cache."""
        for doc in self.collection.find():
            self.cache[doc['_id']] = doc

    def get(self, _id):
        """
        Retrieve a document from the cache.

        Args:
            _id (any): Document ID.

        Returns:
            dict or None: Cached document if it exists.
        """
        return self.cache.get(_id)

    def set(self, _id, data):
        """
        Add or update a document in the cache and queue the update.

        Args:
            _id (any): Document ID.
            data (dict): Document data to cache and persist.

        Example:
            >>> users.set(1234, {"_id": 1234, "name": "Ali"})
        """
        data['_id'] = _id
        self.cache[_id] = data
        self.queue.append(UpdateOne({'_id': _id}, {'$set': data}, upsert=True))

    def flush(self):
        """
        Flush all queued writes to MongoDB using bulk_write.

        Example:
            >>> users.flush()
        """
        if not self.queue:return

        queue_size = len(self.queue)
        start_time = time.time()
        
        try:
            self.collection.bulk_write(list(self.queue))
            elapsed_time = time.time() - start_time
            logger.info(f"Successfully processed {queue_size} updates in {elapsed_time:.2f} seconds")
            self.queue.clear()
            
        except Exception as e:
            logger.error(f"Error during bulk write operation: {str(e)}")
            # Don't clear queue on error so updates can be retried

    def start_auto_flush(self, interval=60):
        """
        Start a background thread to flush updates to MongoDB periodically.

        Args:
            interval (int): Time in seconds between flushes.

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


class Database:
    def __init__(self, db_name: str) -> None:
        uri = os.environ.get("MONGODB_URI")
        db_name = db_name if not LOCAL else "quranbot-dev"
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users = CachedCollection(self.db["users"])
        self.chats = CachedCollection(self.db["chats"])
        self.channels = CachedCollection(self.db["channels"])
        

# --- Example Usage ---
if __name__ == "__main__":
    # Replace with your MongoDB Atlas URI
    password = "0092100921"
    MONGO_URI = f"mongodb+srv://Nusab19:{password}@firstcluster.eh81nbz.mongodb.net/?retryWrites=true&w=majority&appName=FirstCluster"
    client = MongoClient(MONGO_URI)
    db = client["quranbot"]
    logger.info(client.list_database_names())

    users = CachedCollection(db["users"])
    users.set(212, {"name": "Ali", "language": "en"})
    logger.info(f"User 1: {users.get(1)}")

    users.set(222, { "name": "Fatima", "language": "ar"})
    logger.info(f"User 2: {users.get(2)}")

    logger.info(users.get(1))
    logger.info(users.get(212))
    logger.info(users.get(222))

    # users.flush()  # Optional, or use start_auto_flush() for automatic background flush

    # Optional: background flush every 30 seconds
    # users.start_auto_flush(30)

    logger.info("Done.")
