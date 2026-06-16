import os
import urllib.parse
import hashlib
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


def calculate_file_hash(file_path: str) -> str:
    """Generates a SHA-256 hash to uniquely identify file contents."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return ""


def register_ingestion(file_path: str):
    """Creates a master control record in MongoDB using a content hash."""
    file_hash = calculate_file_hash(file_path)

    if not file_hash:
        print("❌ Could not generate file hash. Aborting registration.")
        return None

    collection = get_mongo_db()

    # Check for existing record using the unique hash instead of filepath
    existing_record = collection.find_one({"file_hash": file_hash})

    if existing_record:
        print("⚠️ Record already exists for this file content. Skipping.")
        return existing_record["_id"]

    record = {
        "filename": os.path.basename(file_path),
        "filepath": file_path,
        "file_hash": file_hash,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = collection.insert_one(record)
    print(f"📄 Registered master record in MongoDB: {result.inserted_id}")
    return result.inserted_id


def mark_as_completed(doc_id):
    """Updates the status of a document to 'completed' in MongoDB."""
    if not doc_id:
        return

    collection = get_mongo_db()

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
    # Pointing to the target PDF
    FILE_PATH = "../../data/raw/pdf/1706.03762v7.pdf"

    # Register the file to MongoDB as 'pending'
    doc_id = register_ingestion(FILE_PATH)

    # We DO NOT call mark_as_completed(doc_id) here.
    # The status will remain 'pending' until the ingestion/vectorization
    # module actually finishes its work.
    msg = "".join(
        [
            f"🏁 File {FILE_PATH} is now tracked ",
            "in MongoDB with status: 'pending'.",
        ]
    )
    print(msg)
