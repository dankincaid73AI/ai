import sys
import os
import urllib.parse
from pymongo import MongoClient
import chromadb
import ollama
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🕷️ TARANTULA PROJECT: FULL STACK VERIFICATION 🕷️\n")

# 1. Python Runtime Check
print("1. Checking Python Runtime...")
print(f"    Current Version: {sys.version.split()[0]}")
if sys.version_info.major == 3 and sys.version_info.minor >= 12:
    print("✅ Python 3.12+ confirmed. Optimized environment active.\n")
else:
    print("⚠️ Warning: Not running Python 3.12+")
    print("Check your virtual environment.\n")

# 2. MongoDB Check
print("2. Checking MongoDB Connection...")
try:
    username = urllib.parse.quote_plus(os.getenv("MONGO_USER", ""))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASS", ""))
    host = os.getenv("MONGO_HOST", "localhost:27017")

    safe_mongo_uri = f"mongodb://{username}:{password}@{host}/"
    client = MongoClient(safe_mongo_uri, serverSelectionTimeoutMS=2000)

    # Lightweight ping to verify actual connection
    client.admin.command("ping")
    print("✅ MongoDB connected securely. Ready for state management.\n")
except Exception as e:
    print(f"❌ MongoDB Error: {e}\n")

# 3. ChromaDB Check
print("3. Checking ChromaDB Vector Store...")
try:
    chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
    chroma_client = chromadb.PersistentClient(path=chroma_path)

    # Heartbeat checks if the local SQLite engine is responsive
    chroma_client.heartbeat()
    print(
        f"✅ ChromaDB persistent client active at '{chroma_path}'. "
        "Ready for vectors.\n"
    )
except Exception as e:
    print(f"❌ ChromaDB Error: {e}\n")

# 4. Ollama Check
print("4. Checking Ollama Local Inference Engine...")
try:
    # Attempt to list available models to prove the service is running
    models = ollama.list()
    model_list = models.get("models", [])
    model_names = [m.get("model", m.get("name")) for m in model_list]

    print("✅ Ollama background service is running.")
    if model_names:
        print(f"✅ Available local models: {', '.join(model_names)}\n")
    else:
        print("⚠️ Ollama is running, but no models are downloaded yet.")
        print("   (Run 'ollama run llama3' in terminal to pull one).\n")
except Exception as e:
    print(f"❌ Ollama Error: {e}")
    print("   (Is the Ollama application open and running on your Mac?)\n")

print("==============================================================")
print("If all checks are green, the Tarantula engine is fully online.")
print("==============================================================")
