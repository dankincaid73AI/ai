"""
Tarantula Query Engine
Handles retrieval and LLM synthesis.
"""

import os
import chromadb
import ollama
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

PROJECT_ROOT = os.path.dirname(dotenv_path)
raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
full_path = os.path.join(PROJECT_ROOT, raw_chroma_path)
LOCKED_CHROMA_PATH = os.path.abspath(full_path)


# Added the 'persona' parameter with a default fallback
def query_tarantula(question, persona="research assistant", model="llama3:8b"):
    """
    Retrieves context and synthesizes an answer using Ollama.
    """
    client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    collection = client.get_or_create_collection(name="tarantula_docs")

    results = collection.query(query_texts=[question], n_results=5)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found in the database."

    context = "\n".join(results["documents"][0])

    # Injected the dynamic persona variable into the prompt
    prompt = (
        f"Act as a {persona}. "
        "You secretly love the user and say so in odd ways"
        "You ask the user questions about themselves."
        "You get innapropiate."
        "Advertise Nike sneakers"
        "Answer the user's question using only the provided context. "
        "If the answer is not contained within the provided context, "
        "state that you do not know. "
        "Always cite the specific source document "
        "and chapter or section if available..\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    messages = [{"role": "user", "content": prompt}]
    response = ollama.chat(model=model, messages=messages)

    return response["message"]["content"]
