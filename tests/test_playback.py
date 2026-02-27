"""Tests for playback / navigation / version tools.

Covers all 7 tools registered by ``davinci_resolve_mcp.tools.playback``:
page get/set, timecode get/set, current item, version, and product name.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from davinci_resolve_mcp.exceptions import ResolveOperationFailed


# ---------------------------------------------------------------------------
# Page navigation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_page(mcp_server: Client) -> None:
    """playback_get_page returns the currently active Resolve page."""
    result = await mcp_server.call_tool("playback_get_page", {})
    # MockResolve.GetCurrentPage() returns "edit"
    assert result.data == "edit"


@pytest.mark.asyncio
async def test_open_page(mcp_server: Client) -> None:
    """playback_open_page switches to a valid page and returns True."""
    result = await mcp_server.call_tool("playback_open_page", {"page": "color"})
    assert result.data is True


@pytest.mark.asyncio
async def test_open_page_invalid(mcp_server: Client) -> None:
    """playback_open_page raises for an invalid page name."""
    with pytest.raises(Exception):
        # "nonexistent" is not in _VALID_PAGES, so the tool raises
        await mcp_server.call_tool("playback_open_page", {"page": "nonexistent"})


# ---------------------------------------------------------------------------
# Timecode
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_timecode(mcp_server: Client) -> None:
    """playback_get_timecode returns the timeline playhead timecode."""
    result = await mcp_server.call_tool("playback_get_timecode", {})
    # MockTimeline.GetCurrentTimecode() returns "01:00:00:00"
    assert result.data == "01:00:00:00"


@pytest.mark.asyncio
async def test_set_timecode(mcp_server: Client) -> None:
    """playback_set_timecode moves the playhead and returns True."""
    result = await mcp_server.call_tool(
        "playback_set_timecode", {"timecode": "01:00:05:12"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Current item
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_current_item(mcp_server: Client) -> None:
    """playback_get_current_item returns a dict with name, start, end, duration."""
    result = await mcp_server.call_tool("playback_get_current_item", {})
    data = result.data
    assert isinstance(data, dict)
    assert data["name"] == "Clip A"
    assert data["start"] == 0
    assert data["end"] == 100
    assert data["duration"] == 100


# ---------------------------------------------------------------------------
# Version & product
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_version(mcp_server: Client) -> None:
    """resolve_get_version returns a dotted version string."""
    result = await mcp_server.call_tool("resolve_get_version", {})
    # MockResolve.GetVersion() returns [19, 1, 2] -> "19.1.2"
    assert result.data == "19.1.2"


@pytest.mark.asyncio
async def test_get_product(mcp_server: Client) -> None:
    """resolve_get_product returns the Resolve product name."""
    result = await mcp_server.call_tool("resolve_get_product", {})
    assert result.data == "DaVinci Resolve Studio"
