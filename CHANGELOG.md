# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-27

### Added
- Initial release with 175 tools across 12 domains
- **Phase 1 (Core)**: Playback, project, media storage, media pool, clips, timeline, timeline items, render
- **Phase 2 (Color + Fusion)**: Color grading (nodes, LUTs, CDL, grade versions, color groups), Fusion (compositions, generators, titles, tool listing)
- **Phase 3 (Gallery + Fairlight)**: Gallery (still albums, PowerGrades, grab/import/export), Fairlight (audio insertion, presets)
- **Advanced**: Timeline export (AAF/EDL/FCPXML/OTIO), compound clips, Fusion clips, audio transcription, takes management, database folder CRUD, unique item IDs
- 3 MCP resources: `resolve://system`, `resolve://project`, `resolve://timeline`
- Lazy singleton connection with auto-reconnect on stale references
- Thread-safe connection management with RLock
- Platform auto-detection for macOS, Windows, and Linux scripting module paths
- Pydantic v2 models with CDL validation for structured tool inputs and outputs
- Pagination support for clip lists and timeline item queries
- Shared helpers module to eliminate code duplication across tool domains
- Defensive error handling for version-specific API methods
- `scripts/check_resolve.py` for verifying the Resolve connection
- `scripts/generate_tool_docs.py` for auto-generating tool reference docs
