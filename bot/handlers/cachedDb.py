# written primarily by Claude3.7
# I'll check the code and make sure it works as expected.

import sys
import os
import time
import asyncio
import threading
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from datetime import datetime, timezone
from queue import Queue
from threading import Lock

from pymongo import MongoClient, UpdateOne, InsertOne, DeleteOne
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from bot.utils import getLogger
from bot.utils import getArguments

load_dotenv()

logger = getLogger(__name__)
ARGS = getArguments()
LOCAL = os.environ.get("LOCAL") or ARGS.ARG_LOCAL

# Configure DNS resolver if needed
if LOCAL or ARGS.ARG_FIX_MONGO:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8"]


class CachedCollection:
    """A cached collection that mirrors a MongoDB collection with local in-memory storage.
    
    This class provides a local cache for MongoDB collections, allowing for fast read operations
    and queuing write operations to be executed in bulk at regular intervals.
    
    Example:
        ```python
        # Create a cached collection for users
        users_collection = db['users']
        sync_manager = SyncManager(db)
        cached_users = CachedCollection(users_collection, sync_manager)
        
        # Load initial data
        cached_users._load_initial_data()
        
        # Find a user by ID
        user = cached_users.find_one({"_id": 123456789})
        
        # Find users with specific criteria
        admin_users = cached_users.find({"is_admin": True})
        ```
    """
    
    def __init__(self, collection, sync_manager):
        """Initialize a cached collection.
        
        Args:
            collection: MongoDB collection to mirror
            sync_manager: SyncManager instance to handle background operations
            
        Example:
            ```python
            # Initialize a cached collection for users
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017/")
            db = client.my_database
            sync_manager = SyncManager(db)
            
            # Create cached collection
            users_collection = CachedCollection(db.users, sync_manager)
            ```
        """
        self.collection = collection
        self.sync_manager = sync_manager
        self.cache = {}  # In-memory cache {_id: document}
        self.cache_lock = Lock()  # Thread safety for cache operations
        
    def _load_initial_data(self):
        """Load all documents from MongoDB collection into cache.
        
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            ```python
            # Load all users into cache
            success = users_collection._load_initial_data()
            if success:
                print(f"Loaded {len(users_collection.cache)} users into cache")
            else:
                print("Failed to load users into cache")
            ```
        """
        try:
            documents = list(self.collection.find({}))
            with self.cache_lock:
                for doc in documents:
                    self._id = doc["_id"]
                    self.cache[self._id] = doc
            logger.info(f"Loaded {len(documents)} documents from {self.collection.name}")
            return True
        except PyMongoError as e:
            logger.error(f"Error loading data from {self.collection.name}: {e}")
            return False
    
    def find_one(self, filter_dict: Dict) -> Optional[Dict]:
        """Find a single document in the cache.
        
        Args:
            filter_dict: Filter criteria
            
        Returns:
            Document if found, None otherwise
            
        Example:
            ```python
            # Find a user by ID
            user = users_collection.find_one({"_id": 123456789})
            if user:
                print(f"Found user: {user['_id']}")
                
            # Find a user by username
            user = users_collection.find_one({"username": "john_doe"})
            if user:
                print(f"Found user: {user['username']}")
            ```
        """
        # Simple implementation for _id-based lookups
        if "_id" in filter_dict:
            with self.cache_lock:
                return self.cache.get(filter_dict["_id"])
        
        # For non-_id queries, we need to scan the cache
        with self.cache_lock:
            for doc in self.cache.values():
                match = True
                for k, v in filter_dict.items():
                    if k not in doc or doc[k] != v:
                        match = False
                        break
                if match:
                    return doc
        return None
    
    def find(self, filter_dict: Dict = None) -> List[Dict]:
        """Find documents in the cache.
        
        Args:
            filter_dict: Filter criteria (optional)
            
        Returns:
            List of matching documents
            
        Example:
            ```python
            # Get all users
            all_users = users_collection.find()
            print(f"Total users: {len(all_users)}")
            
            # Find all admin users
            admin_users = users_collection.find({"is_admin": True})
            print(f"Total admin users: {len(admin_users)}")
            
            # Find users with specific settings
            arabic_users = users_collection.find({"settings.primary": "ar"})
            print(f"Users with Arabic as primary language: {len(arabic_users)}")
            ```
        """
        if filter_dict is None:
            filter_dict = {}
            
        results = []
        with self.cache_lock:
            for doc in self.cache.values():
                if not filter_dict:  # Empty filter returns all documents
                    results.append(doc)
                    continue
                    
                match = True
                for k, v in filter_dict.items():
                    if k not in doc or doc[k] != v:
                        match = False
                        break
                if match:
                    results.append(doc)
        return results
    
    def insert_one(self, document: Dict) -> None:
        """Insert a document into the cache and queue for MongoDB.
        
        Args:
            document: Document to insert
            
        Example:
            ```python
            # Insert a new user
            new_user = {
                "_id": 987654321,
                "username": "new_user",
                "settings": {"language": "en", "theme": "dark"},
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
            users_collection.insert_one(new_user)
            
            # Verify insertion
            user = users_collection.find_one({"_id": 987654321})
            print(f"Inserted user: {user['username']}")
            ```
        """
        # Ensure document has _id
        if "_id" not in document:
            raise ValueError("Document must have _id field")
            
        _id = document["_id"]
        
        # Update local cache immediately
        with self.cache_lock:
            self.cache[_id] = document.copy()
        
        # Queue operation for MongoDB
        self.sync_manager.queue_operation(
            self.collection.name,
            "insert_one",
            document
        )
    
    def update_one(self, filter_dict: Dict, update_dict: Dict, upsert: bool = False) -> None:
        """Update a document in the cache and queue for MongoDB.
        
        Args:
            filter_dict: Filter to find document
            update_dict: Update operations
            upsert: Whether to insert if not found
            
        Example:
            ```python
            # Update a user's settings
            users_collection.update_one(
                {"_id": 123456789},
                {"$set": {"settings.language": "fr", "last_active": "2023-01-01"}}
            )
            
            # Update with direct field assignment
            users_collection.update_one(
                {"username": "john_doe"},
                {"status": "active", "login_count": 42}
            )
            
            # Insert if not exists (upsert)
            users_collection.update_one(
                {"_id": 555555555},
                {"$set": {"username": "new_user", "created_at": "2023-01-01"}},
                upsert=True
            )
            ```
        """
        # Handle simple _id-based updates
        if "_id" in filter_dict:
            _id = filter_dict["_id"]
            with self.cache_lock:
                if _id in self.cache:
                    # Apply $set updates
                    if "$set" in update_dict:
                        for k, v in update_dict["$set"].items():
                            self.cache[_id][k] = v
                    
                    # Apply direct updates
                    for k, v in update_dict.items():
                        if not k.startswith("$"):
                            self.cache[_id][k] = v
                elif upsert:
                    # Create new document for upsert
                    new_doc = {"_id": _id}
                    if "$set" in update_dict:
                        new_doc.update(update_dict["$set"])
                    
                    for k, v in update_dict.items():
                        if not k.startswith("$"):
                            new_doc[k] = v
                    
                    self.cache[_id] = new_doc
        
        # Queue operation for MongoDB
        self.sync_manager.queue_operation(
            self.collection.name,
            "update_one",
            filter_dict,
            update_dict,
            upsert
        )
    
    def delete_one(self, filter_dict: Dict) -> None:
        """Delete a document from the cache and queue for MongoDB.
        
        Args:
            filter_dict: Filter to find document to delete
            
        Example:
            ```python
            # Delete a user by ID
            users_collection.delete_one({"_id": 123456789})
            
            # Verify deletion
            user = users_collection.find_one({"_id": 123456789})
            if user is None:
                print("User successfully deleted")
            ```
        """
        # Handle _id-based deletes
        if "_id" in filter_dict:
            _id = filter_dict["_id"]
            with self.cache_lock:
                if _id in self.cache:
                    del self.cache[_id]
        
        # Queue operation for MongoDB
        self.sync_manager.queue_operation(
            self.collection.name,
            "delete_one",
            filter_dict
        )


class SyncManager:
    """Manages synchronization between local cache and MongoDB.
    
    This class handles the background synchronization of cached operations to MongoDB,
    batching operations for efficiency and executing them at regular intervals.
    
    Example:
        ```python
        # Create a sync manager with 30-second sync interval
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/")
        db = client.my_database
        sync_manager = SyncManager(db, sync_interval=30)
        
        # Start the background sync thread
        sync_manager.start()
        
        # Later, when shutting down
        sync_manager.stop()
        ```
    """
    
    def __init__(self, db, sync_interval: int = 60):
        """Initialize the sync manager.
        
        Args:
            db: MongoDB database instance
            sync_interval: Interval in seconds between syncs
            
        Example:
            ```python
            # Create a sync manager with custom interval
            from pymongo import MongoClient
            client = MongoClient("mongodb://localhost:27017/")
            db = client.my_database
            
            # Sync every 15 seconds in development, 60 in production
            is_dev = os.environ.get("ENVIRONMENT") == "development"
            interval = 15 if is_dev else 60
            sync_manager = SyncManager(db, sync_interval=interval)
            ```
        """
        self.db = db
        self.sync_interval = sync_interval
        self.operations_queue = Queue()  # Thread-safe queue for operations
        self.bulk_ops = {}  # Collection name -> list of bulk operations
        self.running = False
        self.sync_thread = None
    
    def start(self):
        """Start the background sync thread.
        
        Example:
            ```python
            # Start the sync manager
            sync_manager = SyncManager(db, sync_interval=30)
            sync_manager.start()
            
            print(f"Sync manager started with {sync_manager.sync_interval}s interval")
            ```
        """
        if self.running:
            return
            
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        logger.info(f"Started sync manager with {self.sync_interval}s interval")
    
    def stop(self):
        """Stop the background sync thread.
        
        Example:
            ```python
            # Stop the sync manager when shutting down
            sync_manager.stop()
            print("Sync manager stopped")
            ```
        """
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5.0)
            logger.info("Stopped sync manager")
    
    def queue_operation(self, collection_name: str, op_type: str, *args):
        """Queue an operation for MongoDB.
        
        Args:
            collection_name: Name of the collection
            op_type: Type of operation (insert_one, update_one, delete_one)
            *args: Arguments for the operation
            
        Example:
            ```python
            # Queue an insert operation
            document = {"_id": 123, "name": "Test"}
            sync_manager.queue_operation("users", "insert_one", document)
            
            # Queue an update operation
            filter_dict = {"_id": 456}
            update_dict = {"$set": {"status": "active"}}
            sync_manager.queue_operation("users", "update_one", filter_dict, update_dict, True)
            
            # Queue a delete operation
            sync_manager.queue_operation("users", "delete_one", {"_id": 789})
            ```
        """
        self.operations_queue.put((collection_name, op_type, args))
    
    def _sync_worker(self):
        """Background worker that processes queued operations.
        
        This method runs in a separate thread and periodically processes the operations queue,
        executing bulk operations against MongoDB at regular intervals defined by sync_interval.
        
        Note: This is an internal method and should not be called directly.
        """
        while self.running:
            # Process all queued operations
            self._process_queue()
            
            # Execute bulk operations
            self._execute_bulk_ops()
            
            # Wait for next sync interval
            time.sleep(self.sync_interval)
    
    def _process_queue(self):
        """Process all operations in the queue and prepare bulk operations.
        
        This method converts queued operations into MongoDB bulk operations
        that can be executed efficiently in a single database call.
        
        Note: This is an internal method and should not be called directly.
        """
        # Initialize bulk operations dict
        self.bulk_ops = {}
        
        # Process all available operations
        while not self.operations_queue.empty():
            try:
                collection_name, op_type, args = self.operations_queue.get(block=False)
                
                # Initialize collection's bulk ops list if needed
                if collection_name not in self.bulk_ops:
                    self.bulk_ops[collection_name] = []
                
                # Convert operation to bulk operation
                if op_type == "insert_one":
                    document = args[0]
                    self.bulk_ops[collection_name].append(InsertOne(document))
                
                elif op_type == "update_one":
                    filter_dict, update_dict, upsert = args[0], args[1], args[2] if len(args) > 2 else False
                    self.bulk_ops[collection_name].append(UpdateOne(filter_dict, update_dict, upsert=upsert))
                
                elif op_type == "delete_one":
                    filter_dict = args[0]
                    self.bulk_ops[collection_name].append(DeleteOne(filter_dict))
                
                self.operations_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing operation: {e}")
    
    def _execute_bulk_ops(self):
        """Execute all prepared bulk operations.
        
        This method sends the prepared bulk operations to MongoDB for execution,
        handling errors and logging the results.
        
        Note: This is an internal method and should not be called directly.
        """
        for collection_name, ops in self.bulk_ops.items():
            if not ops:
                continue
                
            try:
                start_time = time.time()
                collection = self.db[collection_name]
                result = collection.bulk_write(ops, ordered=False)
                end_time = time.time()
                
                logger.info(f"Synced {len(ops)} operations to {collection_name} in {(end_time - start_time) * 1000:.2f}ms")
            except PyMongoError as e:
                logger.error(f"Error executing bulk operations on {collection_name}: {e}")


class CachedDatabase:
    """Main database class that provides cached collections.
    
    This class manages the connection to MongoDB and provides cached collections
    for various data types (users, chats, channels, etc.). It handles initialization,
    data loading, and provides methods for accessing and modifying data.
    
    Example:
        ```python
        # Access the singleton instance
        from bot.handlers.cachedDb import db
        
        # Get a user
        user = db.get_user(123456789)
        print(f"User settings: {user['settings']}")
        
        # Update user settings
        db.update_user_settings(123456789, {"primary": "en", "secondary": "ar"})
        ```
    """
    
    def __init__(self):
        """Initialize the cached database.
        
        Example:
            ```python
            # Create a custom database instance
            custom_db = CachedDatabase()
            
            # Access collections
            users = custom_db.users.find()
            print(f"Loaded {len(users)} users")
            ```
        """
        # Connect to MongoDB
        uri = os.environ.get("MONGODB_URI")
        self.client = MongoClient(uri, server_api=ServerApi("1"))
        
        # Select database based on environment
        if not LOCAL:
            self.db = self.client.quranbot
        else:
            self.db = self.client.quranbot_local
        
        # Default settings
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
        
        # Create sync manager
        sync_interval = 20 if LOCAL else 60
        self.sync_manager = SyncManager(self.db, sync_interval)
        
        # Create cached collections
        self.users = CachedCollection(self.db.users, self.sync_manager)
        self.chats = CachedCollection(self.db.chats, self.sync_manager)
        self.channels = CachedCollection(self.db.channels, self.sync_manager)
        self.activeUsers = CachedCollection(self.db.activeUsers, self.sync_manager)
        self.analytics = CachedCollection(self.db.analytics, self.sync_manager)
        
        # Load initial data
        self._load_initial_data()
        
        # Start sync manager
        if not ARGS.ARG_STOP_THREAD:
            self.sync_manager.start()
        else:
            logger.warning("Database sync thread is stopped by user argument")
    
    def _load_initial_data(self):
        """Load all initial data from MongoDB.
        
        Example:
            ```python
            # Manually reload data
            db._load_initial_data()
            print("All data reloaded from MongoDB")
            ```
        """
        logger.info("Loading initial data from MongoDB...")
        start_time = time.time()
        
        # Load all collections
        self.users._load_initial_data()
        self.chats._load_initial_data()
        self.channels._load_initial_data()
        self.activeUsers._load_initial_data()
        
        end_time = time.time()
        logger.info(f"Loaded all data in {(end_time - start_time) * 1000:.2f}ms")
    
    def get_user(self, user_id: int) -> Dict:
        """Get a user by ID, creating if not exists.
        
        Args:
            user_id: User ID
            
        Returns:
            User document
            
        Example:
            ```python
            # Get an existing user
            user = db.get_user(123456789)
            print(f"User settings: {user['settings']}")
            
            # Get a new user (will be created automatically)
            new_user = db.get_user(987654321)
            print(f"New user created with ID: {new_user['_id']}")
            ```
        """
        user = self.users.find_one({"_id": user_id})
        if not user:
            return self.add_user(user_id)
        return user
    
    def get_chat(self, chat_id: int) -> Dict:
        """Get a chat by ID, creating if not exists.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Chat document
            
        Example:
            ```python
            # Get a chat
            chat = db.get_chat(-100123456789)
            print(f"Chat settings: {chat['settings']}")
            
            # Check if audio is allowed in this chat
            if chat['settings']['allowAudio']:
                print("Audio recitations are allowed in this chat")
            else:
                print("Audio recitations are not allowed in this chat")
            ```
        """
        chat = self.chats.find_one({"_id": chat_id})
        if not chat:
            return self.add_chat(chat_id)
        return chat
    
    def get_channel(self, channel_id: int) -> Dict:
        """Get a channel by ID, creating if not exists.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Channel document
            
        Example:
            ```python
            # Get a channel
            channel = db.get_channel(-100987654321)
            print(f"Channel settings: {channel['settings']}")
            ```
        """
        channel = self.channels.find_one({"_id": channel_id})
        if not channel:
            return self.add_channel(channel_id)
        return channel
    
    def add_user(self, user_id: int) -> Dict:
        """Add a new user.
        
        Args:
            user_id: User ID
            
        Returns:
            New user document
            
        Example:
            ```python
            # Add a new user
            new_user = db.add_user(123456789)
            print(f"Created new user with ID: {new_user['_id']}")
            print(f"Default settings: {new_user['settings']}")
            ```
        """
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        user = {
            "_id": user_id,
            "settings": self.defaultSettings,
            "lastMessageTime": utc_time,
        }
        self.users.insert_one(user)
        return user
    
    def add_chat(self, chat_id: int) -> Dict:
        """Add a new chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            New chat document
            
        Example:
            ```python
            # Add a new group chat
            new_chat = db.add_chat(-100123456789)
            print(f"Created new chat with ID: {new_chat['_id']}")
            print(f"Default settings: {new_chat['settings']}")
            ```
        """
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        chat = {
            "_id": chat_id,
            "settings": self.defaultGroupSettings,
            "lastMessageTime": utc_time,
        }
        self.chats.insert_one(chat)
        return chat
    
    def add_channel(self, channel_id: int) -> Dict:
        """Add a new channel.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            New channel document
            
        Example:
            ```python
            # Add a new channel
            new_channel = db.add_channel(-100987654321)
            print(f"Created new channel with ID: {new_channel['_id']}")
            ```
        """
        channel = {
            "_id": channel_id,
            "settings": self.defaultChannelSettings,
        }
        self.channels.insert_one(channel)
        return channel
    
    def update_user(self, user_id: int, new_data: Dict) -> None:
        """Update user data.
        
        Args:
            user_id: User ID
            new_data: New data to update
            
        Example:
            ```python
            # Update user data
            db.update_user(123456789, {
                "name": "John Doe",
                "language_code": "en",
                "last_active": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Verify update
            user = db.get_user(123456789)
            print(f"Updated user: {user['name']}")
            ```
        """
        self.users.update_one({"_id": user_id}, {"$set": new_data}, upsert=True)
    
    def update_user_settings(self, user_id: int, settings: Dict) -> None:
        """Update user settings.
        
        Args:
            user_id: User ID
            settings: Settings to update
            
        Example:
            ```python
            # Update user settings
            db.update_user_settings(123456789, {
                "primary": "en",  # Change primary language to English
                "secondary": "ar",  # Change secondary language to Arabic
                "font": 2  # Change font to Simple
            })
            
            # Verify settings update
            user = db.get_user(123456789)
            print(f"Updated settings: {user['settings']}")
            ```
        """
        user = self.get_user(user_id)
        updated_settings = {**user["settings"], **settings}
        self.users.update_one({"_id": user_id}, {"$set": {"settings": updated_settings}})
    
    def update_chat_settings(self, chat_id: int, settings: Dict) -> None:
        """Update chat settings.
        
        Args:
            chat_id: Chat ID
            settings: Settings to update
            
        Example:
            ```python
            # Update chat settings
            db.update_chat_settings(-100123456789, {
                "handleMessages": True,  # Enable handling of x:y messages
                "allowAudio": False,  # Disable audio recitations
                "restrictedLangs": ["ar", "en"]  # Restrict to Arabic and English
            })
            
            # Verify settings update
            chat = db.get_chat(-100123456789)
            print(f"Updated chat settings: {chat['settings']}")
            ```
        """
        chat = self.get_chat(chat_id)
        updated_settings = {**chat["settings"], **settings}
        
        # Ensure restricted languages are unique
        if "restrictedLangs" in updated_settings:
            updated_settings["restrictedLangs"] = list(set(updated_settings["restrictedLangs"]))
            
        self.chats.update_one({"_id": chat_id}, {"$set": {"settings": updated_settings}})
    
    def update_channel(self, channel_id: int, settings: Dict) -> None:
        """Update channel settings.
        
        Args:
            channel_id: Channel ID
            settings: Settings to update
            
        Example:
            ```python
            # Update channel settings
            db.update_channel(-100987654321, {
                "language": "en",
                "auto_post": True
            })
            
            # Verify settings update
            channel = db.get_channel(-100987654321)
            print(f"Updated channel settings: {channel['settings']}")
            ```
        """
        channel = self.get_channel(channel_id)
        updated_settings = {**channel["settings"], **settings}
        self.channels.update_one({"_id": channel_id}, {"$set": {"settings": updated_settings}})
    
    def update_active_users(self, user_id: int) -> None:
        """Update active users list.
        
        Args:
            user_id: User ID to add to active users
            
        Example:
            ```python
            # Mark a user as active
            db.update_active_users(123456789)
            
            # Get all active users
            active_users = db.get_active_users()
            print(f"Total active users: {len(active_users)}")
            ```
        """
        self.activeUsers.update_one(
            {"_id": "users"}, 
            {"$addToSet": {"list": user_id}}, 
            upsert=True
        )
    
    def get_active_users(self) -> List[int]:
        """Get list of active users.
        
        Returns:
            List of active user IDs
            
        Example:
            ```python
            # Get all active users
            active_users = db.get_active_users()
            print(f"Total active users: {len(active_users)}")
            
            # Process active users
            for user_id in active_users:
                user = db.get_user(user_id)
                print(f"Active user: {user_id}, settings: {user['settings']}")
            ```
        """
        users_doc = self.activeUsers.find_one({"_id": "users"})
        if not users_doc:
            self.activeUsers.insert_one({"_id": "users", "list": []})
            return []
        return users_doc.get("list", [])
    
    def update_counter(self) -> None:
        """Update analytics counter for today.
        
        Example:
            ```python
            # Increment request counter
            db.update_counter()
            
            # Get today's analytics
            today = time.strftime("%Y-%m-%d")
            analytics = db.analytics.find_one({"_id": today})
            if analytics:
                print(f"Total requests today: {analytics['requests']}")
            ```
        """
        date = time.strftime("%Y-%m-%d")
        self.analytics.update_one(
            {"_id": date}, 
            {"$inc": {"requests": 1}}, 
            upsert=True
        )
    
    def get_all_users(self) -> List[Dict]:
        """Get all users.
        
        Returns:
            List of all user documents
            
        Example:
            ```python
            # Get all users
            all_users = db.get_all_users()
            print(f"Total users: {len(all_users)}")
            
            # Count users by primary language
            language_counts = {}
            for user in all_users:
                lang = user['settings']['primary']
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
            print(f"Users by language: {language_counts}")
            ```
        """
        return self.users.find()
    
    def get_all_chats(self) -> List[Dict]:
        """Get all chats.
        
        Returns:
            List of all chat documents
            
        Example:
            ```python
            # Get all chats
            all_chats = db.get_all_chats()
            print(f"Total chats: {len(all_chats)}")
            
            # Count chats by audio setting
            audio_enabled = sum(1 for chat in all_chats if chat['settings']['allowAudio'])
            print(f"Chats with audio enabled: {audio_enabled}")
            print(f"Chats with audio disabled: {len(all_chats) - audio_enabled}")
            ```
        """
        return self.chats.find()
    
    def get_all_channels(self) -> List[Dict]:
        """Get all channels.
        
        Returns:
            List of all channel documents
            
        Example:
            ```python
            # Get all channels
            all_channels = db.get_all_channels()
            print(f"Total channels: {len(all_channels)}")
            
            # Process channels
            for channel in all_channels:
                print(f"Channel ID: {channel['_id']}")
                print(f"Settings: {channel['settings']}")
            ```
        """
        return self.channels.find()
    
    def get_all_admins(self) -> List[int]:
        """Get all admin user IDs.
        
        Returns:
            List of admin user IDs
            
        Example:
            ```python
            # Get all admin users
            admin_ids = db.get_all_admins()
            print(f"Total admins: {len(admin_ids)}")
            
            # Check if a user is an admin
            user_id = 123456789
            if user_id in admin_ids:
                print(f"User {user_id} is an admin")
            else:
                print(f"User {user_id} is not an admin")
            ```
        """
        admin_users = self.users.find({"is_admin": True})
        return [user["_id"] for user in admin_users]
    
    def force_sync(self) -> None:
        """Force an immediate sync with MongoDB.
        
        Example:
            ```python
            # Make some changes
            db.update_user_settings(123456789, {"primary": "en"})
            db.update_chat_settings(-100123456789, {"allowAudio": False})
            
            # Force immediate sync instead of waiting for the next interval
            db.force_sync()
            print("Changes synced to MongoDB")
            ```
        """
        if self.sync_manager.running:
            # Process queue and execute bulk ops
            self.sync_manager._process_queue()
            self.sync_manager._execute_bulk_ops()
            logger.info("Forced sync completed")
    
    def close(self) -> None:
        """Close the database connection.
        
        Example:
            ```python
            # When shutting down the application
            db.close()
            print("Database connection closed")
            ```
        """
        # Stop sync manager
        self.sync_manager.stop()
        
        # Force final sync
        self.force_sync()
        
        # Close MongoDB connection
        self.client.close()
        logger.info("Database connection closed")


# Create singleton instance
db = CachedDatabase()


# Example usage
async def main():
    # Get some data
    users = db.get_all_users()
    chats = db.get_all_chats()
    print(f"Total Users: {len(users)}")
    print(f"Total Chats: {len(chats)}")
    
    # Test update
    test_user_id = 12345
    db.update_user_settings(test_user_id, {"primary": "en"})
    user = db.get_user(test_user_id)
    print(f"Updated user: {user}")
    
    # Force sync
    db.force_sync()
    
    # Close connection
    db.close()


# Comprehensive example usage
async def comprehensive_example():
    """Demonstrates comprehensive usage of the cached database system."""
    print("\n=== Cached Database Example Usage ===\n")
    
    # 1. Working with users
    print("\n--- Working with Users ---")
    
    # Get or create a user
    user_id = 123456
    user = db.get_user(user_id)
    print(f"User: {user}")
    
    # Update user settings
    db.update_user_settings(user_id, {
        "primary": "en",
        "secondary": "ar",
        "font": 2
    })
    
    # Get updated user
    updated_user = db.get_user(user_id)
    print(f"Updated user settings: {updated_user['settings']}")
    
    # Add custom user data
    db.update_user(user_id, {
        "name": "Example User",
        "language_code": "en",
        "last_active": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # 2. Working with chats
    print("\n--- Working with Chats ---")
    
    # Get or create a chat
    chat_id = -100123456
    chat = db.get_chat(chat_id)
    print(f"Chat: {chat}")
    
    # Update chat settings
    db.update_chat_settings(chat_id, {
        "handleMessages": True,
        "allowAudio": False,
        "restrictedLangs": ["ar", "en", "fr"]
    })
    
    # Get updated chat
    updated_chat = db.get_chat(chat_id)
    print(f"Updated chat settings: {updated_chat['settings']}")
    
    # 3. Working with channels
    print("\n--- Working with Channels ---")
    
    # Get or create a channel
    channel_id = -100654321
    channel = db.get_channel(channel_id)
    print(f"Channel: {channel}")
    
    # Update channel settings
    db.update_channel(channel_id, {
        "language": "en",
        "auto_post": True
    })
    
    # 4. Working with active users
    print("\n--- Working with Active Users ---")
    
    # Mark users as active
    db.update_active_users(user_id)
    db.update_active_users(789012)
    
    # Get active users
    active_users = db.get_active_users()
    print(f"Active users: {active_users}")
    
    # 5. Analytics
    print("\n--- Analytics ---")
    
    # Update counter
    for _ in range(5):
        db.update_counter()
    
    # Get today's analytics
    today = time.strftime("%Y-%m-%d")
    analytics = db.analytics.find_one({"_id": today})
    print(f"Today's analytics: {analytics}")
    
    # 6. Force sync and close
    print("\n--- Sync and Close ---")
    
    # Force sync to MongoDB
    db.force_sync()
    print("Forced sync completed")
    
    # Close connection
    db.close()
    print("Database connection closed")


if __name__ == "__main__":
    # Run the comprehensive example
    asyncio.run(comprehensive_example())
    
    # Or run the simple example
    # asyncio.run(main())