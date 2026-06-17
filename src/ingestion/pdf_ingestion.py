"""PDF Ingestion Module for Project Tarantula.

This module extracts text and metadata from PDF files using
PyMuPDF, splits the text, and ingests it into ChromaDB.
"""

import os
import argparse
import fitz  # PyMuPDF
import chromadb
from dotenv import load_dotenv, find_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
import src.ingestion.track_ingestion as track_ingestion

# 1. Environment & Path Setup
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

PROJECT_ROOT = os.path.dirname(dotenv_path)
raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
full_path = os.path.join(PROJECT_ROOT, raw_chroma_path)
LOCKED_CHROMA_PATH = os.path.abspath(full_path)


def extract_pdf_text(file_path: str) -> str:
    """Extracts raw text from a PDF file page by page."""
    text_content = []
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text_content.append(page.get_text())
        return "\n".join(text_content)
    except Exception as e:
        print(f"❌ Error reading PDF {file_path}: {e}")
        return ""


def process_pdf_pipeline(file_path: str):
    """Orchestrates tracking, extraction, and ChromaDB ingestion."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # 1. Register intent to ingest
    doc_id = str(track_ingestion.register_ingestion(file_path))
    if not doc_id or doc_id == "None":
        print("❌ Failed to register document in MongoDB.")
        return

    print(f"✅ Registered in MongoDB ID: {doc_id}")

    # 2. Connect to ChromaDB
    print(f"🔗 Connecting to ChromaDB at: {LOCKED_CHROMA_PATH}")
    client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    collection = client.get_or_create_collection(name="tarantula_docs")

    # 3. Idempotency Check: Peek for the first chunk
    if len(collection.get(ids=[f"{doc_id}_0"])["ids"]) > 0:
        print(f"⚠️ Chunks for {doc_id} already exist. Skipping.")
        track_ingestion.mark_as_completed(doc_id)
        return

    # 4. Extract the raw data
    print(f"⏳ Extracting text from: {file_path}")
    raw_text = extract_pdf_text(file_path)

    if not raw_text.strip():
        print(f"⚠️ No text from {file_path}. Aborting.")
        return

    # 5. Chunk text using Langchain Splitter
    print("⏳ Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100, length_function=len
    )
    chunks = splitter.split_text(raw_text)

    if not chunks:
        print("⚠️ No chunks generated. Aborting.")
        return

    # 6. Prepare ChromaDB payloads
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = []
    for i in range(len(chunks)):
        metadatas.append({"doc_id": doc_id, "chunk_index": i})

    # 7. Push to ChromaDB
    print(f"⏳ Pushing {len(chunks)} chunks to ChromaDB...")
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    # 8. Complete tracking
    track_ingestion.mark_as_completed(doc_id)
    print(f"✅ Ingested {len(chunks)} chunks. Complete for: {doc_id}")


if __name__ == "__main__":
    desc = "Ingest a PDF file into ChromaDB."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "filepath",
        type=str,
        help="The path to the PDF file to ingest.",
    )

    args = parser.parse_args()
    process_pdf_pipeline(args.filepath)
