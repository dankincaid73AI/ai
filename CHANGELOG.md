# Changelog

All notable changes to **Project Tarantula** will be documented in this file.

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