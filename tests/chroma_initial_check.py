import chromadb


def inspect_collection():
    client = chromadb.PersistentClient(path="./chroma_data")
    collection = client.get_or_create_collection(name="tarantula_docs")

    # 1. Peek: Shows the first 5 records (good for a quick check)
    print("--- 🔍 PEAKING AT FIRST 5 RECORDS ---")
    print(collection.peek(limit=5))

    # 2. Count: How many total chunks are in the DB?
    print(f"\n--- 📊 TOTAL CHUNKS: {collection.count()} ---")

    # 3. Filtered Query: Pull chunks by your doc_id
    # Replace 'YOUR_DOC_ID_HERE' with an actual ID from your MongoDB
    doc_id = "6a1966fdb54e2228a6ec965b"
    results = collection.get(where={"doc_id": doc_id})

    print(f"\n--- 🔗 CHUNKS FOR {doc_id} ---")
    print(f"Found {len(results['ids'])} chunks.")

    # Print the first chunk's content to verify it's the right data
    if results["documents"]:
        print(f"\nFirst chunk snippet:\n{results['documents'][0][:200]}...")


if __name__ == "__main__":
    inspect_collection()
