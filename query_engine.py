"""
Tarantula Query Engine
Handles retrieval and LLM synthesis.
"""

import chromadb
import ollama


def query_tarantula(question, model="llama3:8b"):
    """
    Retrieves context and synthesizes an answer using Ollama.
    """
    # 1. Connect to ChromaDB
    client = chromadb.PersistentClient(path="./chroma_data")
    collection = client.get_or_create_collection(name="tarantula_docs")

    # 2. Retrieve top 3 relevant chunks
    results = collection.query(query_texts=[question], n_results=3)
    context = "\n".join(results["documents"][0])

    # 3. Create the prompt for Ollama
    prompt = (
        "You are an AI assistant powered by Project Tarantula. "
        "Use the provided context to answer the user's question. "
        "If the answer isn't in the context, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    # 4. Define messages separately to satisfy line-length linter
    messages = [{"role": "user", "content": prompt}]

    # 5. Generate response
    response = ollama.chat(model=model, messages=messages)

    return response["message"]["content"]


if __name__ == "__main__":
    USER_QUERY = "What did the author work on before college?"
    print(f"🤖 Querying: {USER_QUERY}...\n")
    print(f"💡 Answer: {query_tarantula(USER_QUERY)}")
