"""URL Ingestion Module for Project Tarantula (Dry Run).

This module extracts text from URLs using Playwright, hashes the URL
to prevent duplicate ingestion, and tracks state in MongoDB.
"""

import argparse
import asyncio
import hashlib
from dotenv import load_dotenv, find_dotenv
from playwright.async_api import async_playwright
import sys
import os

# Get the absolute path of the project root (one directory up from scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to Python's module search path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.ingestion.track_ingestion as track_ingestion  # noqa: E402

# Environment Setup
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


def generate_url_hash(url: str) -> str:
    """Generates a SHA-256 hash of the URL to serve as a unique Document ID."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


async def extract_url_text(url: str) -> str:
    """Extracts raw text from a webpage using Playwright."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print(f"[*] Navigating to target: {url}")
            """  Wait until the network is mostly idle to ensure dynamic
             content loads
            """

            await page.goto(url, wait_until="networkidle")

            # Extract all visible text from the body element
            text_content = await page.locator("body").inner_text()

            await browser.close()
            return text_content
    except Exception as e:
        print(f"❌ Error scraping URL {url}: {e}")
        return ""


async def process_url_pipeline(url: str):
    """Orchestrates tracking and extraction (Dry Run)."""
    if not url:
        print("❌ No URL provided.")
        return

    # 1. Generate SHA-256 Hash for Idempotency
    url_hash = generate_url_hash(url)
    print(f"🔗 URL Hash (SHA-256): {url_hash}")

    # 2. Register intent to ingest in MongoDB
    # Note: Passing the hash alongside the URL allows Mongo to track duplicates
    doc_id = str(track_ingestion.register_ingestion(url))
    if not doc_id or doc_id == "None":
        print("❌ Failed to register document in MongoDB.")
        return

    print(f"✅ Registered in MongoDB ID: {doc_id}")

    # 3. Idempotency Check (ChromaDB)
    print("⚠️ DRY RUN: Skipping ChromaDB connection and idempotency check.")
    # In production, you would check if chunks for doc_id already exist here.

    # 4. Extract the raw data
    print(f"⏳ Extracting text from: {url}")
    raw_text = await extract_url_text(url)

    if not raw_text.strip():
        print(f"⚠️ No text extracted from {url}. Aborting.")
        return

    # 5. Chunk text (Simulated for Dry Run)
    log_prefix = "⏳ DRY RUN: Text extracted successfully."
    print(f"{log_prefix} Total characters: {len(raw_text)}")
    print("⚠️ DRY RUN: Skipping RecursiveCharacterTextSplitter.")

    # 6. Push to ChromaDB (Simulated for Dry Run)
    print("⚠️ DRY RUN: Skipping ChromaDB payload creation and insertion.")

    # 7. Complete tracking
    track_ingestion.mark_as_completed(doc_id)
    print(f"✅ Dry Run Complete. Marked as completed in MongoDB for: {doc_id}")


if __name__ == "__main__":
    desc = "Dry run ingest a URL into MongoDB."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "url",
        type=str,
        help="The URL to scrape and track.",
    )

    args = parser.parse_args()

    """Because Playwright is async, we must run the pipeline inside the
     asyncio event loop
    """
    asyncio.run(process_url_pipeline(args.url))
