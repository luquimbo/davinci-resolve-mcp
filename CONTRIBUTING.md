# Contributing to DaVinci Resolve MCP Server

Thank you for your interest in contributing. This guide covers the development workflow, conventions, and how to add new tools.

## Development Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/luquimbo/davinci-resolve-mcp.git
cd davinci-resolve-mcp
uv sync --dev

# Verify everything works (does not require Resolve running)
uv run pytest
```

## Project Structure

```
src/davinci_resolve_mcp/
  server.py           # FastMCP instance + registration
  resolve_api.py      # Lazy singleton connection to Resolve
  models.py           # Pydantic models
  constants.py        # Enums (pages, track types, colors, ...)
  exceptions.py       # ResolveNotRunning, ResolveOperationFailed
  tools/              # One module per domain (playback, project, ...)
  resources/          # Read-only MCP resources
tests/                # Unit and integration tests
scripts/              # Utility scripts (check_resolve, generate_tool_docs)
```

## Adding a New Tool

1. **Pick the right module.** Tools go in `tools/<domain>.py`. If the tool fits an existing domain, add it there. Only create a new module for a genuinely new API surface.

2. **Follow the registration pattern.** Every tool module exports a `register(mcp)` function. Add your tool inside that function using the `@mcp.tool()` decorator:

```python
@mcp.tool(annotations={"readOnlyHint": True})  # set True if the tool only reads
def my_new_tool(param: str) -> dict:
    """One-line summary of what this tool does.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.
    """
    try:
        api = ResolveAPI.get_instance()
        # ... call Resolve API ...
        return {"result": value}
    except (ResolveNotRunning, ResolveOperationFailed):
        raise
    except AttributeError as exc:
        raise ResolveNotRunning("Lost connection to Resolve ...") from exc
    except Exception as exc:
        raise ResolveOperationFailed("my_new_tool", str(exc)) from exc
```

3. **Use `readOnlyHint`** annotation for tools that do not mutate any state. This helps MCP clients optimize caching and batching.

4. **Handle errors defensively.** Wrap every API call to catch `AttributeError` (stale scripting bridge) and version-specific `AttributeError`s (missing methods in older Resolve versions).

5. **Write tests.** Add unit tests in `tests/` that mock the Resolve API. For tools that require a running Resolve instance, use the `@pytest.mark.integration` marker.

6. **Update the tool count** in `README.md` if your PR adds or removes tools.

## Running Tests

```bash
# All unit tests (no Resolve needed)
uv run pytest

# Integration tests only (requires Resolve running)
uv run pytest -m integration

# With verbose output
uv run pytest -v
```

## Code Style

- Python 3.11+ with type hints on all public functions
- Docstrings on every tool (these become the tool descriptions in MCP)
- `from __future__ import annotations` at the top of every module
- Comments that explain *why*, not *what* (the code explains what)

## Submitting a Pull Request

1. Fork the repository and create a feature branch from `main`
2. Make your changes following the patterns above
3. Run `uv run pytest` and verify all tests pass
4. Regenerate the tool reference: `python scripts/generate_tool_docs.py`
5. Open a PR with a clear description of what changed and why

## Naming Conventions

- Tool functions: `domain_verb_noun` (e.g., `timeline_add_marker`, `color_set_cdl`)
- Read tools: `domain_get_noun` (e.g., `project_get_setting`)
- Write tools: `domain_set_noun` (e.g., `project_set_setting`)
- Delete tools: `domain_delete_noun` (e.g., `render_delete_job`)
- List tools: `domain_get_nouns` (plural) (e.g., `color_get_versions`)
