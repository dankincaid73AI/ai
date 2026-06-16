import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv, find_dotenv
import src.ingestion.track_ingestion as track_ingestion

# 1. Automatically find the .env file anywhere in the project tree
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# 2. Set the Project Root strictly to where the .env file lives
PROJECT_ROOT = os.path.dirname(dotenv_path)

# 3. Pull the CHROMA_PATH and attach it securely to the Project Root
raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
full_path = os.path.join(PROJECT_ROOT, raw_chroma_path)
LOCKED_CHROMA_PATH = os.path.abspath(full_path)


def wipe_file_chunks(collection, doc_id):
    """Wipes all chunks associated with a specific doc_id from ChromaDB."""
    all_docs = collection.get(where={"doc_id": doc_id})
    if all_docs["ids"]:
        collection.delete(ids=all_docs["ids"])
        print(f"🧹 Wiped {len(all_docs['ids'])} duplicate chunks for {doc_id}")


def ingest_text_file(file_path):
    # Fix: Check if file exists BEFORE registering it in the tracker
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Register the ingestion tracking ID
    doc_id = str(track_ingestion.register_ingestion(file_path))

    # Connect using the locked absolute path
    print(f"Connecting to ChromaDB at: {LOCKED_CHROMA_PATH}")
    client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    collection = client.get_or_create_collection(name="tarantula_docs")

    # Idempotency Check: Peek for the first chunk
    if len(collection.get(ids=[f"{doc_id}_0"])["ids"]) > 0:
        print(f"⚠️ Chunks for {doc_id} already exist. Skipping.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100, length_function=len
    )
    chunks = splitter.split_text(text)

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = []
    for i in range(len(chunks)):
        metadatas.append({"doc_id": doc_id, "chunk_index": i})

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    track_ingestion.mark_as_completed(doc_id)
    print(f"✅ Ingested {len(chunks)} chunks. Linked to: {doc_id}")


if __name__ == "__main__":
    FILE_PATH = "./data/raw/text/paul_graham_essay.txt"
    ingest_text_file(FILE_PATH)
