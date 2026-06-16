"""
Tarantula Query Engine
Handles retrieval and LLM synthesis.
"""

import os
import chromadb
import ollama
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


def query_tarantula(question, model="llama3:8b"):
    """
    Retrieves context and synthesizes an answer using Ollama.
    """
    # 1. Connect to ChromaDB using the locked absolute path
    client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    collection = client.get_or_create_collection(name="tarantula_docs")

    # 2. Retrieve top 3 relevant chunks
    results = collection.query(query_texts=[question], n_results=3)

    # Safe extraction to prevent index errors if the database is empty
    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found in the database."

    context = "\n".join(results["documents"][0])

    # 3. Create the prompt for Ollama
    prompt = (
        "Act as a research assistant. "
        "Answer the user's question using only the provided context. "
        "If the answer is not contained within the provided context, "
        "state that you do not know. "
        "Always cite the specific source document "
        "and chapter or section if available..\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    # 4. Define messages separately to satisfy line-length linter
    messages = [{"role": "user", "content": prompt}]

    # 5. Generate response
    response = ollama.chat(model=model, messages=messages)

    return response["message"]["content"]


if __name__ == "__main__":
    USER_QUERY = "What is particulary stand out about Paul?"
    print(f"🤖 Querying: {USER_QUERY}...\n")
    print(f"💡 Answer: {query_tarantula(USER_QUERY)}")
