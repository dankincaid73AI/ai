"""
title: Project Tarantula RAG Tool
author: You
version: 1.0
description: Allows Open WebUI to search the local Tarantula ChromaDB vector
store.
"""

import chromadb


class Tools:
    def __init__(self):
        # This MUST be the container-side path, not your Mac path!
        self.chroma_path = "/app/tarantula_db"

    def search_tarantula(self, query: str) -> str:
        """
        Search the Tarantula local vector database for information from
        ingested PDFs and documents. Use this tool whenever the user asks
        about the Transformer paper, ingested knowledge, or specific document
        metrics.
        :param query: The specific question or search terms to look up in the
        database.
        """
        try:
            # Initialize ChromaDB client pointing to your locked path
            client = chromadb.PersistentClient(path=self.chroma_path)
            collection = client.get_or_create_collection(name="tarantula_docs")

            # Fetch top 5 chunks to avoid semantic blind spots
            results = collection.query(query_texts=[query], n_results=5)

            if not results.get("documents") or not results["documents"][0]:
                return "No relevant context found in the Tarantula database."

            # Assemble the retrieved chunks and inject metadata for citation
            context_chunks = []
            for idx, text in enumerate(results["documents"][0]):
                doc_id = "Unknown"
                if results.get("metadatas") and results["metadatas"][0]:
                    # Extracted to a variable to satisfy line-length limits
                    metadata = results["metadatas"][0][idx]
                    doc_id = metadata.get("doc_id", "Unknown")

                context_chunks.append(f"[Source ID: {doc_id}]\n{text}")

            context = "\n\n".join(context_chunks)

            # Return raw text and strict instructions to the LLM
            return (
                f"Retrieved Context from Tarantula DB:\n\n{context}\n\n"
                "SYSTEM DIRECTIVE: Answer the user's question using ONLY the "
                "context above. Always cite the specific Source ID in your "
                "answer."
            )

        except Exception as e:
            return f"Error accessing Tarantula database: {str(e)}"
