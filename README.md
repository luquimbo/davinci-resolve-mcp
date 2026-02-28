# DaVinci Resolve MCP Server

The most complete MCP server for DaVinci Resolve's Scripting API. Control projects, timelines, media, color grading, rendering, and more from any MCP-compatible client.

## Features

- **158 tools** across 12 domains (playback, project, media storage, media pool, clips, timelines, timeline items, render, color, Fusion, gallery, Fairlight)
- **3 resources** for quick context (`resolve://system`, `resolve://project`, `resolve://timeline`)
- **Complete API coverage** of the DaVinci Resolve Scripting API (Phases 1-3)
- **Pydantic v2 models** for type-safe inputs and outputs
- **Pagination** for large clip and timeline item lists
- **Auto-reconnect** if Resolve restarts or becomes unresponsive
- **Platform auto-detection** for macOS, Windows, and Linux

## Requirements

- DaVinci Resolve 18+ (Free or Studio)
- Python 3.11+
- macOS, Windows, or Linux

## Quick Start

### Install from PyPI

```bash
pip install davinci-resolve-mcp
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install davinci-resolve-mcp
```

### Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp"
    }
  }
}
```

Then restart Claude Desktop. DaVinci Resolve must be running for tools to work.

See [docs/CLAUDE_DESKTOP.md](docs/CLAUDE_DESKTOP.md) for a detailed setup guide with troubleshooting.

### Development Setup

```bash
git clone https://github.com/lucasacadevor/davinci-resolve-mcp.git
cd davinci-resolve-mcp
uv sync --dev
uv run davinci-resolve-mcp
```

### Verify Your Setup

```bash
python scripts/check_resolve.py
```

This prints Resolve version, current project, and timeline info to confirm the scripting bridge is working.

## Tool Domains

| Domain | Module | Tools | Description |
|--------|--------|------:|-------------|
| Playback | `playback` | 7 | Page navigation, timecode, playhead position, version info |
| Project | `project` | 13 | CRUD, settings, import/export (.drp), database folder navigation |
| Media Storage | `media_storage` | 4 | Browse mounted volumes, list files, import to media pool |
| Media Pool | `media_pool` | 14 | Folder CRUD, clip management, timeline creation, metadata export |
| Clips | `media_pool_item` | 16 | Clip metadata, properties, colors, markers, flags, proxy linking |
| Timeline | `timeline` | 22 | CRUD, tracks (add/delete/rename/lock), items, markers, duplication |
| Timeline Items | `timeline_item` | 18 | Transform, crop, composite, color labels, markers, flags, linking |
| Render | `render` | 14 | Formats, codecs, presets, job queue, start/stop, progress monitoring |
| Color | `color` | 22 | Nodes, LUTs, CDL, grade versions, DRX application, color groups |
| Fusion | `fusion` | 11 | Compositions CRUD, generators, titles, tool listing |
| Gallery | `gallery` | 14 | Still albums, grab/import/export stills, PowerGrades, grade application |
| Fairlight | `fairlight` | 3 | Audio insertion, presets listing, preset application |

**Resources** (read-only context, no tool call needed):

| URI | Description |
|-----|-------------|
| `resolve://system` | Resolve version, product name, current page |
| `resolve://project` | Project name, timeline count, resolution, frame rate |
| `resolve://timeline` | Timeline name, frame range, track counts, timecode |

## Architecture

```
src/davinci_resolve_mcp/
  server.py          FastMCP instance, registers all modules, CLI entry point
  resolve_api.py     Lazy singleton with platform auto-detection and health checks
  models.py          Pydantic models (CDLValues for ASC color correction)
  constants.py       Enums for pages, track types, clip colors, marker colors, export types
  exceptions.py      ResolveNotRunning, ResolveOperationFailed
  tools/
    playback.py      Page navigation, timecode, version
    project.py       Project CRUD, settings, folders, import/export
    media_storage.py Volume browsing, file listing, import
    media_pool.py    Folder CRUD, clip management, timeline creation
    media_pool_item.py  Clip metadata, properties, markers, flags
    timeline.py      Timeline CRUD, tracks, items, markers
    timeline_item.py Transform, crop, composite, color, markers
    render.py        Formats, codecs, presets, jobs, rendering
    color.py         Nodes, LUTs, CDL, versions, groups
    fusion.py        Compositions, generators, titles
    gallery.py       Stills, albums, PowerGrades
    fairlight.py     Audio insertion, presets
  resources/
    system_info.py   resolve://system
    project_info.py  resolve://project
    timeline_info.py resolve://timeline
```

**Key patterns:**

- **Lazy singleton** (`ResolveAPI`): Connects to Resolve on first access, not at import time. A `GetVersion()` health check runs on every access to detect stale references and reconnect automatically.
- **One module per domain**: Each tool module exports a `register(mcp)` function that decorates tool functions with `@mcp.tool()`.
- **Defensive error handling**: Every API call catches `AttributeError` (stale scripting bridge) and re-raises as `ResolveNotRunning`. Version-specific methods are wrapped so missing APIs return clear errors instead of crashes.
- **Pagination**: Large lists (clips, timeline items) support `offset` and `limit` parameters, returning `has_more` to signal additional pages.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design document.

## Testing

```bash
# Unit tests (no Resolve needed)
uv run pytest

# Integration tests (requires Resolve running)
uv run pytest -m integration
```

## Scope

All 158 tools ship in v0.1.0 — covering core editing, color grading, Fusion compositions, gallery stills, and Fairlight audio.

## Auto-Generated Tool Reference

Run the following to generate a complete tool reference from the registered MCP tools:

```bash
python scripts/generate_tool_docs.py
```

This creates `docs/TOOLS.md` with every tool name, description, parameters, and return type grouped by domain.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
