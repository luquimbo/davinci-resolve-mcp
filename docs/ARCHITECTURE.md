# Architecture

This document describes the internal design of the DaVinci Resolve MCP Server: how it connects to Resolve, how tools are organized, how errors are handled, and the conventions that keep the codebase consistent.

## Module Structure

```
src/davinci_resolve_mcp/
|
|-- server.py              Entry point. Creates the FastMCP instance, imports all
|                          tool and resource modules, calls register(mcp) on each,
|                          and exposes main() as the CLI command.
|
|-- resolve_api.py         Lazy singleton (ResolveAPI) that manages the connection
|                          to the running Resolve instance. Platform auto-detection
|                          adds the correct scripting modules path before importing
|                          DaVinciResolveScript.
|
|-- models.py              Pydantic v2 models for structured data:
|                          MarkerInfo, ClipInfo, TimelineInfo, TimelineItemInfo,
|                          RenderSettings, RenderJobInfo, PaginatedResult, CDLValues.
|
|-- constants.py           Enums: ResolvePage, TrackType, CompositeMode, ClipColor,
|                          MarkerColor, FlagColor, ExportType, TimelineExportSubtype.
|                          Also lists commonly used project setting keys.
|
|-- exceptions.py          ResolveNotRunning (connection lost or Resolve not open)
|                          ResolveOperationFailed (API call returned error/None)
|
|-- tools/                 One module per Resolve API domain. Each exports register(mcp).
|   |-- playback.py            7 tools: page nav, timecode, version
|   |-- project.py            13 tools: CRUD, settings, import/export, folders
|   |-- media_storage.py       4 tools: volumes, files, import to pool
|   |-- media_pool.py         14 tools: folders, clips, timelines, metadata
|   |-- media_pool_item.py    16 tools: clip metadata, properties, markers, flags
|   |-- timeline.py           22 tools: CRUD, tracks, items, markers, duplication
|   |-- timeline_item.py      18 tools: transform, crop, composite, markers, flags
|   |-- render.py             14 tools: formats, codecs, presets, jobs, rendering
|   |-- color.py              22 tools: nodes, LUTs, CDL, versions, groups
|   |-- fusion.py             11 tools: compositions, generators, titles
|   |-- gallery.py            14 tools: albums, stills, PowerGrades
|   |-- fairlight.py           3 tools: audio insertion, presets
|
|-- resources/             Read-only MCP resources (no tool call needed).
    |-- system_info.py         resolve://system  (version, product, page)
    |-- project_info.py        resolve://project (name, timelines, resolution, fps)
    |-- timeline_info.py       resolve://timeline (name, frames, tracks, timecode)
```

## Connection Management

### Lazy Singleton

`ResolveAPI` is a classic singleton. The connection to DaVinci Resolve is not established at import time or server startup. Instead, it connects on the first tool call that accesses any `ResolveAPI` property.

```
Tool call --> ResolveAPI.get_instance() --> _ensure_connected()
                                               |
                                    [Has cached reference?]
                                       /              \
                                     Yes               No
                                      |                 |
                              [Health check:        [_connect():
                               GetVersion()]         load script module,
                                  |                  call scriptapp("Resolve")]
                           [Succeeds?]                  |
                            /       \              [Returns resolve obj
                          Yes       No              or raises
                           |         |              ResolveNotRunning]
                      [Return    [Drop ref,
                       cached]    reconnect]
```

### Platform Auto-Detection

`_get_modules_path()` returns the platform-specific directory where Resolve installs its scripting modules:

| Platform | Path |
|----------|------|
| macOS | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/` |
| Windows | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\` |
| Linux | `/opt/resolve/Developer/Scripting/Modules/` |

The path is inserted into `sys.path` and the `RESOLVE_SCRIPT_API` / `RESOLVE_SCRIPT_LIB` environment variables are set before `DaVinciResolveScript` is dynamically imported.

### Health Check and Auto-Reconnect

Every property access on `ResolveAPI` (`.resolve`, `.project`, `.timeline`, etc.) runs through `_ensure_connected()`, which:

1. If a cached reference exists, calls `GetVersion()` as a cheap health check.
2. If the health check raises any exception (stale reference after Resolve restart), drops the cached reference and reconnects.
3. If no cached reference exists, performs a fresh connection.

This means the MCP server survives Resolve restarts without any manual intervention.

## Tool Registration Pattern

Every tool module follows the same structure:

```python
# tools/example.py

from __future__ import annotations
from fastmcp import FastMCP
from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI

def register(mcp: FastMCP) -> None:
    """Register all <domain> tools on *mcp*."""

    @mcp.tool(annotations={"readOnlyHint": True})
    def example_get_something() -> str:
        """Tool docstring becomes the MCP tool description."""
        try:
            api = ResolveAPI.get_instance()
            # ... call Resolve API ...
            return result
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning("Lost connection ...") from exc
        except Exception as exc:
            raise ResolveOperationFailed("example_get_something", str(exc)) from exc
```

**Why closures inside `register()`?** This keeps tool functions scoped to their domain module and avoids polluting the module namespace. The `@mcp.tool()` decorator registers them on the shared FastMCP instance at import time.

**Why `readOnlyHint`?** MCP clients can use this annotation to batch or cache read-only calls, and to warn users before executing mutating operations.

In `server.py`, registration is a simple loop:

```python
for mod in _TOOL_MODULES:
    mod.register(mcp)
```

## Error Handling Strategy

Two custom exceptions cover all failure modes:

| Exception | When | Example |
|-----------|------|---------|
| `ResolveNotRunning` | Resolve is not open, scripting bridge is stale, or the scripting module cannot be imported | `GetVersion()` raises `AttributeError` after Resolve was restarted |
| `ResolveOperationFailed` | An API call returned `None`, `False`, or an unexpected value | `CreateProject("name")` returns `None` because the name is taken |

Every tool wraps its API calls in a try/except chain with this priority:

1. **Re-raise known exceptions** (`ResolveNotRunning`, `ResolveOperationFailed`) immediately.
2. **Catch `AttributeError`** and re-raise as `ResolveNotRunning` (stale scripting bridge).
3. **Catch all other exceptions** and wrap in `ResolveOperationFailed` with the tool name and error detail.

For version-specific APIs (Gallery, Fairlight, some Color methods), the pattern is slightly different: `AttributeError` from a missing method returns a clear error message rather than crashing.

## Pagination Approach

Tools that return potentially large lists (clips in a folder, items on a track) accept `offset` and `limit` parameters:

```python
@mcp.tool(annotations={"readOnlyHint": True})
def media_pool_get_clips(offset: int = 0, limit: int = 50) -> dict:
```

The return value follows a consistent paginated structure:

```json
{
  "items": [...],
  "total": 250,
  "offset": 0,
  "limit": 50,
  "has_more": true
}
```

**Why server-side pagination?** The Resolve scripting API always returns full lists. Pagination happens after the full list is fetched, slicing with `all_items[offset:offset+limit]`. This prevents sending thousands of clip descriptions in a single MCP response, which could exceed token limits or slow down LLM processing.

## Naming Conventions

### Tool Names

Tool names follow the pattern `domain_verb_noun`:

| Pattern | Example | Meaning |
|---------|---------|---------|
| `domain_get_noun` | `project_get_setting` | Read a single value |
| `domain_get_nouns` | `color_get_versions` | Read a list |
| `domain_set_noun` | `timeline_set_name` | Write a single value |
| `domain_create_noun` | `media_pool_create_folder` | Create a new entity |
| `domain_delete_noun` | `render_delete_job` | Delete an entity |
| `domain_add_noun` | `clip_add_marker` | Add an item to a collection |
| `domain_verb_noun` | `render_start`, `gallery_grab_still` | Action-oriented |

### Parameters

- `item_name`, `clip_name`: Display name used to look up objects by linear scan.
- `track_type`: Always `"video"`, `"audio"`, or `"subtitle"`.
- `track_index`: Always 1-based (matching Resolve's API convention).
- `offset` / `limit`: Pagination parameters (0-based offset, default limit 50).

### Helpers

Internal helper functions are prefixed with underscore and are module-private:

- `_find_item()`: Locate a timeline item by name on a track.
- `_find_clip()`: Locate a media pool clip by name in the current folder.
- `_require_pool()`: Get the media pool or raise.
- `_require_timeline()`: Get the current timeline or raise.
- `_require_project()`: Get the current project or raise.

These helpers reduce boilerplate across tool functions within the same module.
