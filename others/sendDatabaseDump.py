import os
import json
import pymongo
import requests
import io
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "5596148289"
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "quranbot"


def custom_serializer(obj):
    """Convert datetime and ObjectId to a serializable format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def export_database():
    """
    Export the MongoDB database as a JSON file stored in RAM.

    Returns:
        dict: A dictionary containing:
            - file_buffer (BytesIO): JSON export in memory.
            - collections_count (int): Number of collections.
            - docs_count (int): Total number of documents.
    """
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collections = db.list_collection_names()
    db_export = {}

    for collection_name in collections:
        collection = db[collection_name]
        documents = list(collection.find({}))

        for doc in documents:
            if "_id" in doc and not isinstance(doc["_id"], str):
                doc["_id"] = str(doc["_id"])

        db_export[collection_name] = documents

    json_data = json.dumps(db_export, default=custom_serializer)
    file_buffer = io.BytesIO(json_data.encode())  # Store in RAM

    return {
        "file_buffer": file_buffer,
        "collections_count": len(collections),
        "docs_count": sum(len(docs) for docs in db_export.values()),
    }


def send_file_telegram(file_info):
    """
    Send the exported database JSON file to a Telegram chat.

    Args:
        file_info (dict): Dictionary containing the file buffer, collection count, and document count.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = f"""\
<b>Database:</b> <code>{DB_NAME}</code> of @@AlFurqanRobot

📅 Time: <b>{timestamp}</b>
📂 Collections: <b>{file_info['collections_count']}</b>
📄 Total Documents: <b>{file_info['docs_count']}</b>
"""

    file_info["file_buffer"].seek(0)  # Reset buffer position

    print("Sending database dump to Telegram...")
    response = requests.post(
        url,
        files={"document": ("alQuranBot.json", file_info["file_buffer"])},
        data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
    )

    if response.status_code == 200:
        print("Database dump sent successfully!")
    else:
        print(f"Failed to send. Error: {response.text}")


def main():
    """Main function to export and send the database dump to Telegram."""
    try:
        print("Exporting database...")
        file_info = export_database()

        send_file_telegram(file_info)
        print("Process completed successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
