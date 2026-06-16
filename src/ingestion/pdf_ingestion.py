"""
PDF Ingestion Module for Project Tarantula.

This module is responsible for extracting text and metadata from
PDF files using PyMuPDF and preparing them for vectorization.
"""

import argparse
import fitz  # PyMuPDF
from src.ingestion.track_ingestion import register_ingestion, mark_as_completed


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
    """Orchestrates tracking, extraction, vectorization, and completion."""
    # 1. Register intent to ingest (Status: Pending)
    doc_id = register_ingestion(file_path)
    if not doc_id:
        return

    # 2. Extract the raw data
    print(f"⏳ Extracting text from: {file_path}")
    raw_text = extract_pdf_text(file_path)

    if not raw_text.strip():
        print(f"⚠️ No text extracted from {file_path}. " "Aborting pipeline.")
        return

    # 3. Vectorize and push to ChromaDB
    print("⏳ Chunking and storing in ChromaDB...")
    # NOTE: chunk_and_store should return a boolean success flag
    # chroma_success = chunk_and_store(doc_id, file_path, raw_text)
    chroma_success = True  # Placeholder until Chroma logic is wired

    # 4. Close the loop ONLY if ChromaDB succeeds
    if chroma_success:
        mark_as_completed(doc_id)
    else:
        msg = "".join(
            [
                f"❌ ChromaDB ingestion failed for {file_path}. ",
                "MongoDB status remains 'pending'.",
            ]
        )
        print(msg)


if __name__ == "__main__":
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Ingest a PDF file into Project Tarantula."
    )

    # 2. Add the file path argument
    parser.add_argument(
        "filepath",
        type=str,
        help="The relative or absolute path to the PDF file to ingest.",
    )

    # 3. Parse the CLI inputs
    args = parser.parse_args()

    # 4. Pass the user-provided path to your pipeline
    process_pdf_pipeline(args.filepath)
