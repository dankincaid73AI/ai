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
    """Generates a SHA-256 hash to uniquely identify local file contents."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return ""


def calculate_url_hash(url: str) -> str:
    """Generates a SHA-256 hash to uniquely identify a URL."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def register_ingestion(source: str):
    """Creates a master control record in MongoDB using a content hash."""

    # Determine if the source is a URL or a local file path
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        content_hash = calculate_url_hash(source)
        source_name = source  # Use the URL as the identifier name
        source_type = "url"
    else:
        content_hash = calculate_file_hash(source)
        source_name = os.path.basename(source)
        source_type = "file"

    if not content_hash:
        print(f"❌ Hash failed for {source}. Aborting.")

    collection = get_mongo_db()

    # Check for existing record using the unique hash
    # Note: keeping the key as 'file_hash' to maintain backwards compatibility
    # with any existing database records, but it represents the content hash.
    existing_record = collection.find_one({"file_hash": content_hash})

    if existing_record:
        print("⚠️ Record already exists for this content. Skipping.")
        return existing_record["_id"]

    record = {
        "filename": source_name,
        "filepath": source,
        "file_hash": content_hash,
        "source_type": source_type,
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

    # Perform the update - THIS defines the 'result' variable
    result = collection.update_one(filter_query, new_values)

    if result.modified_count > 0:
        print(f"✅ MongoDB updated: {doc_id} marked as 'completed'.")
    elif result.matched_count > 0:
        print(f"✅ MongoDB checked: {doc_id} is already marked as 'completed'.")
    else:
        print(f"⚠️ Warning: Could not find record {doc_id} to update.")


if __name__ == "__main__":
    # Test pointing to a target PDF
    FILE_PATH = "../../data/raw/pdf/1706.03762v7.pdf"
    doc_id_file = register_ingestion(FILE_PATH)

    # Test pointing to a target URL
    URL_PATH = "https://quotes.toscrape.com"
    doc_id_url = register_ingestion(URL_PATH)
