import os
import urllib.request

# Configuration
TARGET_DIR = "./data/raw/text"
DATA_URL = (
    "https://raw.githubusercontent.com/run-llama/llama_index/main/"
    "docs/examples/data/paul_graham/paul_graham_essay.txt"
)
FILE_PATH = os.path.join(TARGET_DIR, "paul_graham_essay.txt")


def fetch_sample_data():
    """Downloads the baseline testing dataset into the raw data partition."""
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"📁 Created directory structure: {TARGET_DIR}")

    if os.path.exists(FILE_PATH):
        print(f"⏭️ File already exists at {FILE_PATH}. Skipping download.")
        return

    print(f"🌐 Fetching sample data from {DATA_URL}...")
    try:
        urllib.request.urlretrieve(DATA_URL, FILE_PATH)
        file_size = os.path.getsize(FILE_PATH) / 1024
        print(
            f"✅ Successfully downloaded dataset to {FILE_PATH} "
            f"({file_size:.2f} KB)"
        )
    except Exception as e:
        print(f"❌ Download failed: {e}")


if __name__ == "__main__":
    fetch_sample_data()
