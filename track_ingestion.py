import os
import urllib.parse
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


def get_mongo_uri():
    """Constructs a secure MongoDB URI from environment variables."""
    user = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASS", ""))
    host = os.getenv("MONGO_HOST", "localhost:27017")

    if user and password:
        return f"mongodb://{user}:{password}@{host}/?authSource=admin"
    return f"mongodb://{host}/"


def register_ingestion(file_path: str):
    """Creates a master control record in MongoDB for tracking."""
    # Initialize connection using the dynamic URI
    client = MongoClient(get_mongo_uri())
    db = client[os.getenv("MONGO_DB_NAME", "tarantula_db_v1")]
    collection = db["ingestion_logs"]

    # Create the control document using timezone-aware UTC
    record = {
        "filename": os.path.basename(file_path),
        "filepath": file_path,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Insert and return the unique MongoDB ID
    result = collection.insert_one(record)
    print(f"📄 Registered master record in MongoDB: {result.inserted_id}")
    return result.inserted_id


if __name__ == "__main__":
    # Test execution for the Paul Graham file
    FILE_PATH = "./data/raw/text/paul_graham_essay.txt"
    doc_id = register_ingestion(FILE_PATH)
    print(f"🏁 Master record established: {doc_id}")
