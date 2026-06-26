"""URL Ingestion Module for Project Tarantula.

This module extracts text from URLs using Playwright, chunks the text,
and ingests it into ChromaDB while tracking state in MongoDB.
"""

import os
import argparse
import asyncio
import hashlib
import chromadb
from dotenv import load_dotenv, find_dotenv
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter
import src.ingestion.track_ingestion as track_ingestion

# Environment Setup
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

PROJECT_ROOT = os.path.dirname(dotenv_path)
raw_chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
full_path = os.path.join(PROJECT_ROOT, raw_chroma_path)
LOCKED_CHROMA_PATH = os.path.abspath(full_path)


def generate_url_hash(url: str) -> str:
    """Generates a SHA-256 hash to serve as a unique Document ID."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


async def extract_url_text(url: str) -> str:
    """Extracts raw text from a webpage using Playwright."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print(f"[*] Navigating to target: {url}")

            # Wait until network is mostly idle for dynamic content
            await page.goto(url, wait_until="networkidle")

            # Extract all visible text from the body element
            text_content = await page.locator("body").inner_text()

            await browser.close()
            return text_content
    except Exception as e:
        print(f"❌ Error scraping URL {url}: {e}")
        return ""


async def process_url_pipeline(url: str):
    """Orchestrates tracking, extraction, and ChromaDB ingestion."""
    if not url:
        print("❌ No URL provided.")
        return

    # 1. Generate SHA-256 Hash
    url_hash = generate_url_hash(url)
    print(f"🔗 URL Hash (SHA-256): {url_hash}")

    # 2. Register intent to ingest
    doc_id = str(track_ingestion.register_ingestion(url))
    if not doc_id or doc_id == "None":
        print("❌ Failed to register document in MongoDB.")
        return

    print(f"✅ Registered in MongoDB ID: {doc_id}")

    # 3. Connect to ChromaDB
    print(f"🔗 Connecting to ChromaDB at: {LOCKED_CHROMA_PATH}")
    client = chromadb.PersistentClient(path=LOCKED_CHROMA_PATH)
    collection = client.get_or_create_collection(name="tarantula_docs")

    # 4. Idempotency Check
    if len(collection.get(ids=[f"{doc_id}_0"])["ids"]) > 0:
        print(f"⚠️ Chunks for {doc_id} already exist. Skipping.")
        track_ingestion.mark_as_completed(doc_id)
        return

    # 5. Extract the raw data
    print(f"⏳ Extracting text from: {url}")
    raw_text = await extract_url_text(url)

    if not raw_text.strip():
        print(f"⚠️ No text extracted from {url}. Aborting.")
        return

    # 6. Chunk text
    print("⏳ Chunking text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100, length_function=len
    )
    chunks = splitter.split_text(raw_text)

    if not chunks:
        print("⚠️ No chunks generated. Aborting.")
        return

    # 7. Prepare ChromaDB payloads
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = []
    for i in range(len(chunks)):
        metadatas.append({"doc_id": doc_id, "chunk_index": i})

    # 8. Push to ChromaDB
    print(f"⏳ Pushing {len(chunks)} chunks to ChromaDB...")
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    # 9. Complete tracking
    track_ingestion.mark_as_completed(doc_id)
    print(f"✅ Ingested {len(chunks)} chunks. Complete for: {doc_id}")


if __name__ == "__main__":
    desc = "Ingest a URL into ChromaDB."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "url",
        type=str,
        help="The URL to scrape and ingest.",
    )

    args = parser.parse_args()

    # Run the pipeline inside the asyncio event loop
    asyncio.run(process_url_pipeline(args.url))
