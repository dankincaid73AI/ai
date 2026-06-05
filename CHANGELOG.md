# Changelog

All notable changes to **Project Tarantula** will be documented in this file.

## [1.1.3] - 2026-06-05
### Changed
- **Project Architecture:** Executed a comprehensive restructuring of the root directory to separate concerns, improve scalability, and establish a production-ready repository.
- **Core Engine Migration:** Relocated primary pipeline logic from the root directory into a newly established `src/` directory tree.
- **Test Isolation:** Migrated all validation and database check scripts (`check_mongo.py`, `chroma_initial_check.py`, `pre_ingestion_db_test.py`, `stack_verification.py`) into a dedicated `tests/` directory.

### Added
- **Source Subdirectories:** Implemented `src/db/`, `src/ingestion/`, and `src/query/` to isolate database connectivity, data processing, and retrieval operations.
- **Data Subdirectories:** Established a `data/raw/` directory structure for local file processing.

## [1.1.2] - 2026-06-05
### Added
- Created `main.py` entry point to serve as an interactive terminal Command Line Interface (CLI).
- Implemented an infinite query loop (`while True`) featuring clean termination commands (`quit`, `exit`).
- Added user experience feedback states including status markers ("Thinking...") and formatted output markers.

### Changed
- Integrated CLI directly with the root-level `query_engine.py` module to streamline execution from the project root directory.

### Verified
- Confirmed strict prompt constraint compliance; system correctly reports an absence of data in the vector store rather than fallback hallucination.
- Validated keyboard interrupt handling (`Ctrl + C`) for abrupt termination.

## [1.1.1] - 2026-06-05
### Added
- **Query Engine:** Implemented `query_engine.py` to enable local Retrieval-Augmented Generation (RAG) using Ollama.
- **Local Inference:** Integrated local LLM support, allowing synthesis of retrieved context without external API dependencies.

### Fixed
- **Code Quality:** Refactored `query_engine.py` to strictly adhere to PEP 8/Flake8 linting standards[cite: 1.
- **Error Handling:** Added local model existence verification to catch 404 response errors during Ollama communication[cite: 1.

## [1.1.0] - 2026-06-05
### Added
- **Idempotency Guardrails:** Implemented pre-ingestion checks in ChromaDB to prevent vector duplication.
- **Status Synchronization:** Automated MongoDB document status transitions from `pending` to `completed` post-vectorization.
- **Maintenance Utilities:** Added `wipe_file_chunks` to allow surgical deletion of specific document vectors.

### Fixed
- **Architectural Refactor:** Centralized MongoDB connection logic into `track_ingestion.py` for improved modularity.
- **Data Integrity:** Resolved potential race conditions in ingestion by adding strict `ObjectId` handling.
- **Code Quality:** Standardized formatting to comply with PEP 8 and Flake8 linter requirements.

## [1.0.2-alpha] - 2026-05-29
### Added
- Implemented `track_ingestion.py` for registering ingestion tasks in MongoDB with timezone-aware UTC timestamps.
- Added connection verification and system health-check logic for database pipelines.
- Integrated `urllib.parse` for secure, dynamic MongoDB URI generation to handle special characters in credentials.
- Created `check_mongo.py` utility for auditing ingestion logs and verifying data persistence.

### Fixed
- Resolved `DeprecationWarning` regarding `datetime.utcnow()` by migrating to `datetime.now(timezone.utc)`.

## [1.0.1-alpha] - 2026-05-28
### Added
- Established structured local directories (`data/raw/text/`) to isolate source files by format type.
- Created a `fetch_data.py` utility script to download the baseline Paul Graham essay dataset for text ingestion validation.

## [1.0.0-alpha] - 2026-05-26
### Added
- Initialized Dockerized MongoDB environment.
- Added dynamic password URL-encoding for secure MongoDB URI generation.
- Initialized persistent ChromaDB vector storage configuration.
- Added `db_setup.py` for automated database and collection bootstrapping.
- Implemented `stack_verification.py` for automated local environment health checks.
- Defined dependency management via `requirements.txt`.
- Created `.env.example` template for configuration environment variables.
- Configured `.gitignore` to prevent exposure of sensitive credentials and local artifacts.
- Created `/images` directory for architectural documentation and visual assets.

### Changed
- Refactored `.env` structure to isolate `MONGO_USER` and `MONGO_PASS` variables.

### Fixed
- Updated .gitignore to remove .DS_Store from any future commit.