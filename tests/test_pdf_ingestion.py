"""PDF Ingestion Module for Project Tarantula.

This module extracts text from PDF files and chunks the data
in memory to prepare for vectorization.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Opens a PDF and extracts raw text page by page."""
    extracted_pages = []
    try:
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            raw_text = page.get_text().strip()

            if raw_text:  # Only append pages with text
                extracted_pages.append(
                    {
                        "page_number": page_num + 1,
                        "text": raw_text,
                    }
                )
        return extracted_pages
    except Exception as e:
        print(f"\n❌ Error reading PDF: {e}")
        return []
    finally:
        if "doc" in locals():
            doc.close()


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:
    """Splits text into chunks with a defined character overlap."""

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move start pointer forward, minus overlap to retain context
        start += chunk_size - overlap

    return chunks


def run_poc(file_path: str):
    """Executes a dry-run of the ingestion pipeline."""
    print(f"\n⚙️  Starting Ingestion POC for: {file_path}")
    print("-" * 50)

    # 1. Extraction
    pages = extract_text_from_pdf(file_path)
    if not pages:
        print("No text extracted. Exiting POC.")
        return

    print(f"✅ Extracted {len(pages)} pages of text.")

    # 2. Chunking
    all_chunks = []
    for page in pages:
        page_chunks = chunk_text(page["text"])
        for i, chunk in enumerate(page_chunks):
            all_chunks.append(
                {
                    "page_number": page["page_number"],
                    "chunk_index": i + 1,
                    "text_preview": chunk[:100].replace("\n", " ") + "...",
                    "length": len(chunk),
                }
            )

    print(f"✅ Processed into {len(all_chunks)} total chunks.")
    print("\n🔍 --- CHUNK PAYLOAD PREVIEW ---")

    # 3. Visual Verification (Print the first 3 chunks to inspect)
    for chunk in all_chunks[:3]:
        print(
            f"\nPage {chunk['page_number']} | "
            f"Chunk {chunk['chunk_index']} | "
            f"Size: {chunk['length']} chars"
        )
        print(f"Text: {chunk['text_preview']}")

    print("\n" + "-" * 50)
    print("🏁 POC Complete. Data is ready for ChromaDB embedding.")


if __name__ == "__main__":
    # Pointing to the Attention Is All You Need paper
    test_pdf = "./data/raw/pdf/1706.03762v7.pdf"
    run_poc(test_pdf)
