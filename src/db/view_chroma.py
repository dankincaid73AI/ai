import os
import chromadb
from dotenv import load_dotenv, find_dotenv

# 1. Automatically find the .env file anywhere in the project tree
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# 2. Set the Project Root strictly to where the .env file lives
PROJECT_ROOT = os.path.dirname(dotenv_path)

# 3. Pull the CHROMA_PATH and attach it securely to the Project Root
raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
full_path = os.path.join(PROJECT_ROOT, raw_chroma_path)
LOCKED_CHROMA_PATH = os.path.abspath(full_path)


def inspect_database(target_collection=None):
    # Use the strictly locked absolute path defined above
    print(f"Connecting to ChromaDB at: {LOCKED_CHROMA_PATH}...\n")

    try:
        client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    # 4. List all available collections
    try:
        collections = client.list_collections()
    except Exception as e:
        print(f"Error accessing database collections: {e}")
        return

    if not collections:
        print("Database connected, but no collections were found.")
        return

    print(f"Available Collections: {[c.name for c in collections]}\n")

    # 5. Default to the first collection if one isn't specified
    if not target_collection:
        target_collection = collections[0].name

    print(f"--- Displaying contents of: '{target_collection}' ---")

    try:
        collection = client.get_collection(name=target_collection)
    except Exception as e:
        print(f"Could not load collection '{target_collection}': {e}")
        return

    # 6. Fetch the data
    all_data = collection.get()
    total_records = len(all_data["ids"])

    print(f"Total chunks indexed: {total_records}\n")
    print("=" * 60)

    # 7. Loop through and print each chunk
    for i in range(total_records):
        print(f"ID:        {all_data['ids'][i]}")
        print(f"Metadata: {all_data['metadatas'][i]}")
        print(f"Text:     {all_data['documents'][i]}\n")
        print("-" * 60)


if __name__ == "__main__":
    inspect_database("tarantula_docs")
