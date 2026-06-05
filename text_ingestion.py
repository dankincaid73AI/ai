import os
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import track_ingestion

load_dotenv()


def wipe_file_chunks(collection, doc_id):
    """Wipes all chunks associated with a specific doc_id from ChromaDB."""
    # Chroma allows querying/deleting by IDs
    # Since we prefixed IDs with doc_id, we can find them
    # Note: This is a simplified approach; in production,
    # you might use get() to fetch all matching IDs first.
    all_docs = collection.get(where={"doc_id": doc_id})
    if all_docs["ids"]:
        collection.delete(ids=all_docs["ids"])
        print(f"🧹 Wiped {len(all_docs['ids'])} duplicate chunks for {doc_id}")


def ingest_text_file(file_path):
    doc_id = str(track_ingestion.register_ingestion(file_path))
    client = chromadb.PersistentClient(path="./chroma_data")
    collection = client.get_or_create_collection(name="tarantula_docs")

    # Idempotency Check: Peek for the first chunk
    if len(collection.get(ids=[f"{doc_id}_0"])["ids"]) > 0:
        print(f"⚠️ Chunks for {doc_id} already exist. Skipping.")
        return

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
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
