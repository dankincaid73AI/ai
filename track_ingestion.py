import os
import urllib.parse
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

# Load variables
load_dotenv()


def get_mongo_db():
    """Returns the database connection collection."""
    user = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASS", ""))
    host = os.getenv("MONGO_HOST", "localhost:27017")

    if user and password:
        uri = f"mongodb://{user}:{password}@{host}/?authSource=admin"
    else:
        uri = f"mongodb://{host}/"

    client = MongoClient(uri)
    db = client[os.getenv("MONGO_DB_NAME", "tarantula_db_v1")]
    return db["ingestion_logs"]


def register_ingestion(file_path: str):
    """Creates a master control record in MongoDB."""
    collection = get_mongo_db()
    existing_record = collection.find_one({"filepath": file_path})

    if existing_record:
        print(f"⚠️ Record already exists for {file_path}. Skipping.")
        return existing_record["_id"]

    record = {
        "filename": os.path.basename(file_path),
        "filepath": file_path,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = collection.insert_one(record)
    print(f"📄 Registered master record in MongoDB: {result.inserted_id}")
    return result.inserted_id


def mark_as_completed(doc_id):
    """Updates the status of a document to 'completed' in MongoDB."""
    collection = get_mongo_db()  # Get the collection anew

    # Ensure doc_id is an ObjectId if it isn't one already
    query_id = ObjectId(doc_id) if not isinstance(doc_id, ObjectId) else doc_id

    # Define the update components clearly
    filter_query = {"_id": query_id}
    new_values = {"$set": {"status": "completed"}}

    # Perform the update
    result = collection.update_one(filter_query, new_values)

    if result.modified_count > 0:
        print(f"✅ MongoDB updated: {doc_id} marked as 'completed'.")
    else:
        print(f"⚠️ Warning: Could not update record {doc_id}.")


if __name__ == "__main__":
    FILE_PATH = "./data/raw/text/paul_graham_essay.txt"
    doc_id = register_ingestion(FILE_PATH)
    # Testing the update
    mark_as_completed(doc_id)
