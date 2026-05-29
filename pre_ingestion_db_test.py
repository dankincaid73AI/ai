import os
import sys
import urllib.parse
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import chromadb

# Load environment variables
load_dotenv()

# Securely construct MongoDB URI
MONGO_USER = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
MONGO_PASS = urllib.parse.quote_plus(os.getenv("MONGO_PASS", ""))
MONGO_HOST = os.getenv("MONGO_HOST", "localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "tarantula_db_v1")

if MONGO_USER and MONGO_PASS:
    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}/"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}/"

# File Paths
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")
FILE_PATH = "./data/raw/text/paul_graham_essay.txt"


def verify_connections():
    """Step 1: Establish and verify all database connections (Fail Fast)."""
    print("🔍 Verifying database connections...")

    # 1. Test MongoDB Connection
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        mongo_client.admin.command("ping")
        print(f"✅ MongoDB connected to host: {MONGO_HOST}")
    except ConnectionFailure:
        print("❌ MongoDB connection failed. Is the Docker container running?")
        sys.exit(1)

    # 2. Test ChromaDB Initialization
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        print(f"✅ ChromaDB initialized securely at {CHROMA_PATH}.")
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        sys.exit(1)

    return mongo_client, chroma_client


if __name__ == "__main__":
    print("🚀 Starting Tarantula Ingestion Pipeline...")
    mongo, chroma = verify_connections()
    print("\n🏁 Step 1 Complete. Infrastructure is ready for data flow.")
