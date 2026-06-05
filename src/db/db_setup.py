import os
import urllib.parse
import chromadb
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Safely encode the username and password
username = urllib.parse.quote_plus(os.getenv("MONGO_USER"))
password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
host = os.getenv("MONGO_HOST")

# Construct the safe connection string
safe_mongo_uri = f"mongodb://{username}:{password}@{host}/"

# 2. Force MongoDB creation by inserting a placeholder document
mongo_client = MongoClient(safe_mongo_uri)
db = mongo_client[os.getenv("MONGO_DB_NAME")]

# MongoDB creates the DB and Collection the moment a document is written
db["system_logs"].insert_one({"status": "database_initialized"})
print(f"✅ MongoDB '{os.getenv('MONGO_DB_NAME')}' created and initialized.")

# 3. Force ChromaDB creation by initializing the persistent client
chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))
collection = chroma_client.get_or_create_collection(name="tarantula_vectors")
collection.add(documents=["initialization_vector"], ids=["init_id"])
print(
    f"✅ ChromaDB database created at '{os.getenv('CHROMA_PATH')}' "
    f"with collection 'tarantula_vectors'."
)
