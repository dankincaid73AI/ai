import os
import urllib.parse
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_mongo_uri():
    """Constructs the secure MongoDB URI."""
    user = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASS", ""))
    host = os.getenv("MONGO_HOST", "localhost:27017")

    if user and password:
        return f"mongodb://{user}:{password}@{host}/?authSource=admin"
    return f"mongodb://{host}/"


def list_ingestion_logs():
    """Queries and prints all records in the ingestion_logs collection."""
    client = MongoClient(get_mongo_uri())
    db = client[os.getenv("MONGO_DB_NAME", "tarantula_db_v1")]
    collection = db["ingestion_logs"]

    print(f"🔍 Searching collection: 'ingestion_logs' in '{db.name}'...\n")

    # Fetch all documents
    cursor = collection.find({})

    count = 0
    for doc in cursor:
        print(doc)
        count += 1

    if count == 0:
        print("📭 The collection is empty.")
    else:
        print(f"\n🏁 Found {count} record(s).")


if __name__ == "__main__":
    list_ingestion_logs()
