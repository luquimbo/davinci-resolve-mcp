#!/usr/bin/env python3
"""Auto-generate docs/TOOLS.md from the registered MCP tools.

Creates a FastMCP instance, registers all tool and resource modules,
then iterates over every registered tool to extract its name, description,
parameters, and return type.  The output is a markdown file grouped by
domain, written to docs/TOOLS.md.

Usage:
    python scripts/generate_tool_docs.py

The script does NOT require DaVinci Resolve to be running.  It only
inspects the tool registration metadata, not the Resolve API itself.
"""

from __future__ import annotations

import inspect
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, get_type_hints

# Add the src directory to the path so we can import without installing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Import all tool modules (same list as server.py)
from davinci_resolve_mcp.tools import (
    playback,
    project,
    media_storage,
    media_pool,
    media_pool_item,
    timeline,
    timeline_item,
    render,
    color,
    fusion,
    gallery,
    fairlight,
)

# FastMCP is needed to create a throwaway server instance for introspection
from fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Domain metadata: maps module to a human-readable domain name and description
# ---------------------------------------------------------------------------
_DOMAIN_ORDER: list[tuple[str, str, Any]] = [
    ("Playback", "Page navigation, timecode, playhead, version info", playback),
    ("Project", "Project CRUD, settings, import/export, database folders", project),
    ("Media Storage", "Browse volumes, list files, import to media pool", media_storage),
    ("Media Pool", "Folder CRUD, clip management, timeline creation, metadata", media_pool),
    ("Clips (Media Pool Item)", "Clip metadata, properties, colors, markers, flags, proxy", media_pool_item),
    ("Timeline", "Timeline CRUD, tracks, items, markers, duplication", timeline),
    ("Timeline Items", "Transform, crop, composite, color labels, markers, flags", timeline_item),
    ("Render", "Formats, codecs, presets, job queue, rendering, progress", render),
    ("Color", "Nodes, LUTs, CDL, grade versions, DRX, color groups", color),
    ("Fusion", "Compositions CRUD, generators, titles, tool listing", fusion),
    ("Gallery", "Still albums, grab/import/export stills, PowerGrades", gallery),
    ("Fairlight", "Audio insertion, presets listing, preset application", fairlight),
]


def _extract_tools_from_module(mcp: FastMCP, module: Any) -> list[dict]:
    """Register a module's tools on a fresh MCP instance and extract metadata.

    This creates tool registrations by calling module.register(mcp), then
    inspects the registered tools to build metadata dicts.

    Returns a list of dicts with keys: name, description, parameters, return_type, read_only.
    """
    # Snapshot the tool names before registration so we can find what was added
    # FastMCP stores tools internally; we'll collect them after all registrations
    pass  # We register all at once, then filter by name prefix


def _get_param_info(func: Any) -> list[dict]:
    """Extract parameter names, types, and defaults from a function signature.

    Returns a list of dicts with keys: name, type, default, description.
    """
    sig = inspect.signature(func)
    params = []

    for param_name, param in sig.parameters.items():
        # Skip 'self' and internal params
        if param_name in ("self", "cls"):
            continue

        # Get the type annotation as a string
        if param.annotation is inspect.Parameter.empty:
            type_str = "Any"
        else:
            ann = param.annotation
            # Handle string annotations and complex types
            if isinstance(ann, str):
                type_str = ann
            elif hasattr(ann, "__name__"):
                type_str = ann.__name__
            elif hasattr(ann, "__origin__"):
                # Handle generic types like list[str], dict, etc.
                type_str = str(ann).replace("typing.", "")
            else:
                type_str = str(ann).replace("typing.", "")

        # Get the default value
        if param.default is inspect.Parameter.empty:
            default_str = "*required*"
        elif param.default is None:
            default_str = "`None`"
        else:
            default_str = f"`{param.default!r}`"

        params.append({
            "name": param_name,
            "type": type_str,
            "default": default_str,
        })

    return params


def _get_return_type(func: Any) -> str:
    """Extract the return type annotation from a function."""
    sig = inspect.signature(func)
    if sig.return_annotation is inspect.Signature.empty:
        return "Any"

    ann = sig.return_annotation
    if isinstance(ann, str):
        return ann
    if hasattr(ann, "__name__"):
        return ann.__name__
    return str(ann).replace("typing.", "")


def _get_first_line(docstring: str | None) -> str:
    """Extract the first non-empty line from a docstring."""
    if not docstring:
        return "(no description)"

    for line in docstring.strip().split("\n"):
        line = line.strip()
        if line:
            return line

    return "(no description)"


def main() -> None:
    """Generate docs/TOOLS.md from the registered MCP tools."""

    # Create a throwaway FastMCP instance for tool registration introspection
    mcp = FastMCP("DaVinci Resolve (doc generation)")

    # Register all modules (same order as server.py)
    tool_modules_ordered = []
    for domain_name, domain_desc, module in _DOMAIN_ORDER:
        # Count tools before and after registration to identify which belong to this module
        # We need to track tools per domain, so we register one module at a time
        pass

    # Register all modules at once on the shared instance
    for _name, _desc, module in _DOMAIN_ORDER:
        module.register(mcp)

    # Now collect all registered tools. FastMCP stores tools in an internal registry.
    # We'll group them by prefix to map back to domains.
    #
    # Since tools are registered as closures, we need to inspect the MCP's internal
    # tool list. FastMCP v2 stores tools differently than v1, so we try both.

    # Approach: re-register one module at a time on separate instances to get
    # per-domain tool lists.
    domain_tools: list[tuple[str, str, list[dict]]] = []

    for domain_name, domain_desc, module in _DOMAIN_ORDER:
        # Create a fresh MCP per module to isolate its tools
        temp_mcp = FastMCP(f"temp-{domain_name}")
        module.register(temp_mcp)

        # Extract registered tools from the temp MCP instance.
        # FastMCP v2 uses ._tool_manager._tools or .list_tools()
        tools_info: list[dict] = []

        # Try to access the internal tool registry
        registered_tools = {}
        if hasattr(temp_mcp, "_tool_manager"):
            # FastMCP v2 pattern
            tm = temp_mcp._tool_manager
            if hasattr(tm, "_tools"):
                registered_tools = tm._tools
            elif hasattr(tm, "tools"):
                registered_tools = tm.tools
        elif hasattr(temp_mcp, "_tools"):
            registered_tools = temp_mcp._tools

        if not registered_tools:
            # Fallback: try the public list_tools if available (async, not suitable here)
            # Instead, look for tools as attributes
            pass

        for tool_name, tool_obj in registered_tools.items():
            # Extract metadata from the tool object
            # The tool object varies by FastMCP version; try common attributes
            description = "(no description)"
            func = None

            if hasattr(tool_obj, "fn"):
                func = tool_obj.fn
            elif hasattr(tool_obj, "func"):
                func = tool_obj.func
            elif callable(tool_obj):
                func = tool_obj

            if hasattr(tool_obj, "description"):
                description = tool_obj.description or ""
            elif func and func.__doc__:
                description = _get_first_line(func.__doc__)

            # Extract parameters and return type from the function signature
            params = _get_param_info(func) if func else []
            return_type = _get_return_type(func) if func else "Any"

            # Check if read-only
            read_only = False
            if hasattr(tool_obj, "annotations"):
                annotations = tool_obj.annotations
                if isinstance(annotations, dict):
                    read_only = annotations.get("readOnlyHint", False)

            tools_info.append({
                "name": tool_name,
                "description": description,
                "parameters": params,
                "return_type": return_type,
                "read_only": read_only,
            })

        # Sort tools alphabetically within each domain
        tools_info.sort(key=lambda t: t["name"])
        domain_tools.append((domain_name, domain_desc, tools_info))

    # ------------------------------------------------------------------
    # Generate the markdown output
    # ------------------------------------------------------------------
    output_path = Path(__file__).resolve().parent.parent / "docs" / "TOOLS.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_tools = sum(len(tools) for _, _, tools in domain_tools)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []
    lines.append("# Tool Reference")
    lines.append("")
    lines.append(f"Auto-generated on {now} by `scripts/generate_tool_docs.py`.")
    lines.append("")
    lines.append(f"**{total_tools} tools** across **{len(domain_tools)} domains**.")
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for domain_name, _desc, tools in domain_tools:
        anchor = domain_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        lines.append(f"- [{domain_name}](#{anchor}) ({len(tools)} tools)")
    lines.append("")

    # One section per domain
    for domain_name, domain_desc, tools in domain_tools:
        lines.append(f"## {domain_name}")
        lines.append("")
        lines.append(f"*{domain_desc}*")
        lines.append("")

        if not tools:
            lines.append("*No tools registered for this domain.*")
            lines.append("")
            continue

        for tool in tools:
            # Tool header
            ro_badge = " `read-only`" if tool["read_only"] else ""
            lines.append(f"### `{tool['name']}`{ro_badge}")
            lines.append("")
            lines.append(tool["description"])
            lines.append("")

            # Parameters table
            if tool["parameters"]:
                lines.append("| Parameter | Type | Default |")
                lines.append("|-----------|------|---------|")
                for p in tool["parameters"]:
                    lines.append(f"| `{p['name']}` | `{p['type']}` | {p['default']} |")
                lines.append("")

            # Return type
            lines.append(f"**Returns:** `{tool['return_type']}`")
            lines.append("")

    # Write the file
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path} with {total_tools} tools across {len(domain_tools)} domains.")


if __name__ == "__main__":
    main()
