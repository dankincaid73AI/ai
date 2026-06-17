"""PDF Ingestion Module for Project Tarantula.

This module extracts text and metadata from PDF files using
PyMuPDF and prepares them for vectorization.
"""

import argparse
import fitz  # PyMuPDF
from src.ingestion.track_ingestion import register_ingestion


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
    """Orchestrates tracking and visual chunking validation."""
    # 1. Register intent to ingest (Status: Pending)
    doc_id = register_ingestion(file_path)
    if not doc_id:
        print("❌ Failed to register document in MongoDB.")
        return

    print(f"✅ Registered in MongoDB ID: {doc_id}")
    print("(Status: pending)")

    # 2. Extract the raw data
    print(f"⏳ Extracting text from: {file_path}")
    raw_text = extract_pdf_text(file_path)

    if not raw_text.strip():
        print(f"⚠️ No text from {file_path}. Aborting.")
        return

    # 3. DRY RUN: Chunk the file and output to terminal
    print("\n--- 🛠️ DRY RUN: Executing Text Chunking ---")

    chunk_size = 1000
    chunk_overlap = 200

    words = raw_text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            overlap_count = max(1, int(chunk_overlap / 10))
            # Slice with no surrounding whitespace to satisfy linters
            current_chunk = current_chunk[-overlap_count:]
            current_length = sum(len(w) + 1 for w in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Print out the chunks sequentially for audit
    for idx, chunk in enumerate(chunks):
        print(f"\n--- [ Chunk {idx + 1} ] ---")
        print(f"Length: {len(chunk)} chars")
        print(chunk)
        print("-" * 40)

    print(f"\n🚀 Split text into {len(chunks)} chunks.")
    print("🛑 Pipeline paused: No ChromaDB write executed.")
    print("MongoDB status remains 'pending'.")


if __name__ == "__main__":
    desc = "Ingest a PDF file (Dry Run Mode)."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "filepath",
        type=str,
        help="The path to the PDF file to ingest.",
    )

    args = parser.parse_args()
    process_pdf_pipeline(args.filepath)
