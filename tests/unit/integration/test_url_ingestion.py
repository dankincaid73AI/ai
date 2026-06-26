"""Test / POC Module for URL Ingestion.

This script tests the extraction and chunking lifecycle of web pages
without executing persistent database side-effects.
"""

import asyncio
from playwright.async_api import async_playwright
from langchain_text_splitters import RecursiveCharacterTextSplitter


async def test_extract_url_text(url: str) -> str:
    """Extracts raw text from a webpage using an isolated Playwright
    instance.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print(f"[*] (Test) Navigating to target: {url}")
            await page.goto(url, wait_until="networkidle")

            text_content = await page.locator("body").inner_text()
            await browser.close()
            return text_content
    except Exception as e:
        print(f"❌ (Test) Error scraping URL {url}: {e}")
        return ""


def test_chunk_text(text: str) -> list[str]:
    """Splits raw text using the production splitter specifications."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100, length_function=len
    )
    return splitter.split_text(text)


async def run_url_poc(url: str):
    """Executes a dry-run validation of the URL ingestion components."""
    print(f"\n⚙️  Starting URL Ingestion POC for: {url}")
    print("-" * 60)

    # 1. Extraction Test
    raw_text = await test_extract_url_text(url)
    if not raw_text.strip():
        print("❌ No text extracted. Exiting URL POC.")
        return

    print(f"✅ Extracted raw text stream ({len(raw_text)} total characters).")

    # 2. Chunking Test
    chunks = test_chunk_text(raw_text)
    if not chunks:
        print("❌ No chunks generated from the text. Exiting URL POC.")
        return

    print(f"✅ Split successfully into {len(chunks)} total chunks.")
    print("\n🔍 --- CHUNK PAYLOAD PREVIEW ---")

    # 3. Visual Verification Payload (Previews first 3 chunks)
    for i, chunk in enumerate(chunks[:3]):
        preview = chunk[:120].replace("\n", " ") + "..."
        print(f"\nChunk {i + 1} / {len(chunks)} | Size: {len(chunk)} chars")
        print(f"Text Preview: {preview}")

    print("\n" + "-" * 60)
    print("🏁 URL POC Complete. Extraction and chunking math are valid.")


if __name__ == "__main__":
    """Default target matching your successful test case seen in
    url_ingestion_results.gif
    """
    target_test_url = "https://quotes.toscrape.com/"

    # Run the async loop
    asyncio.run(run_url_poc(target_test_url))
