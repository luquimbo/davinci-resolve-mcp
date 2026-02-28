#!/usr/bin/env python3
"""Auto-generate docs/TOOLS.md from the registered MCP tools.

Creates a FastMCP instance per domain, registers each tool module, then
uses the async list_tools() API to extract every tool's name, description,
input schema, and annotations.  The output is a markdown file grouped by
domain, written to docs/TOOLS.md.

Usage:
    python scripts/generate_tool_docs.py

The script does NOT require DaVinci Resolve to be running.  It only
inspects the tool registration metadata, not the Resolve API itself.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add the src directory to the path so we can import without installing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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
from fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Domain metadata: maps module to a human-readable domain name and description
# ---------------------------------------------------------------------------
_DOMAIN_ORDER: list[tuple[str, str, Any]] = [
    ("Playback", "Page navigation, timecode, playhead, version info", playback),
    ("Project", "Project CRUD, settings, import/export, database folders, archive/restore", project),
    ("Media Storage", "Browse volumes, list files, import to media pool", media_storage),
    ("Media Pool", "Folder CRUD, clip management, timeline creation, metadata", media_pool),
    ("Clips (Media Pool Item)", "Clip metadata, properties, colors, markers, flags, proxy, transcription", media_pool_item),
    ("Timeline", "Timeline CRUD, tracks, items, markers, export, compound/Fusion clips, settings", timeline),
    ("Timeline Items", "Transform, crop, composite, color labels, markers, flags, takes, stabilize", timeline_item),
    ("Render", "Formats, codecs, presets, job queue, rendering, progress", render),
    ("Color", "Nodes, LUTs, CDL, grade versions, DRX, color groups, node labels", color),
    ("Fusion", "Compositions CRUD, generators, titles, tool listing", fusion),
    ("Gallery", "Still albums, grab/import/export stills, PowerGrades", gallery),
    ("Fairlight", "Audio insertion, presets listing, preset application", fairlight),
]


def _format_type(schema_prop: dict) -> str:
    """Convert a JSON Schema property to a human-readable type string."""
    if "anyOf" in schema_prop:
        # Union type — collect non-null types
        types = [t.get("type", "any") for t in schema_prop["anyOf"] if t.get("type") != "null"]
        if not types:
            return "any"
        return " | ".join(types)

    prop_type = schema_prop.get("type", "any")

    # Handle array types with items
    if prop_type == "array":
        items = schema_prop.get("items", {})
        item_type = items.get("type", "any")
        return f"list[{item_type}]"

    # Handle object types
    if prop_type == "object":
        return "dict"

    return prop_type


def _extract_params(input_schema: dict) -> list[dict]:
    """Extract parameter info from a JSON Schema input_schema."""
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))
    params = []

    for name, prop in properties.items():
        type_str = _format_type(prop)
        default = "*required*" if name in required else f"`{prop.get('default', 'None')!r}`"
        description = prop.get("description", "")
        params.append({
            "name": name,
            "type": type_str,
            "default": default,
            "description": description,
        })

    return params


async def _collect_domain_tools(domain_name: str, module: Any) -> list[dict]:
    """Register a module on a fresh FastMCP and extract its tools via list_tools()."""
    temp_mcp = FastMCP(f"temp-{domain_name}")
    module.register(temp_mcp)

    # list_tools() returns FunctionTool objects with .name, .description,
    # .parameters (JSON Schema dict), .annotations (ToolAnnotations)
    tools = await temp_mcp.list_tools()
    tools_info = []

    for tool in tools:
        # Extract parameters from the JSON Schema in .parameters
        params = _extract_params(tool.parameters or {})

        # Check for read-only annotation (ToolAnnotations has .readOnlyHint)
        read_only = False
        if tool.annotations is not None:
            read_only = bool(getattr(tool.annotations, "readOnlyHint", False))

        # Use the full description from the tool
        desc = tool.description or "(no description)"

        tools_info.append({
            "name": tool.name,
            "description": desc,
            "parameters": params,
            "read_only": read_only,
        })

    # Sort alphabetically within each domain
    tools_info.sort(key=lambda t: t["name"])
    return tools_info


async def async_main() -> None:
    """Generate docs/TOOLS.md from the registered MCP tools."""

    # Collect tools per domain (each in its own FastMCP instance for isolation)
    domain_tools: list[tuple[str, str, list[dict]]] = []

    for domain_name, domain_desc, module in _DOMAIN_ORDER:
        tools = await _collect_domain_tools(domain_name, module)
        domain_tools.append((domain_name, domain_desc, tools))

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
            # Tool header with optional read-only badge
            ro_badge = " `read-only`" if tool["read_only"] else ""
            lines.append(f"### `{tool['name']}`{ro_badge}")
            lines.append("")
            lines.append(tool["description"])
            lines.append("")

            # Parameters table
            if tool["parameters"]:
                lines.append("| Parameter | Type | Default | Description |")
                lines.append("|-----------|------|---------|-------------|")
                for p in tool["parameters"]:
                    desc = p["description"].replace("|", "\\|")  # Escape pipes
                    lines.append(f"| `{p['name']}` | `{p['type']}` | {p['default']} | {desc} |")
                lines.append("")

    # Write the file
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path} with {total_tools} tools across {len(domain_tools)} domains.")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
