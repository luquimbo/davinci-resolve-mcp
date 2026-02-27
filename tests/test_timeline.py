"""Tests for timeline tools.

Covers 11 key tools registered by ``davinci_resolve_mcp.tools.timeline``:
get/set current, count, get/set name, track count, add track, items pagination,
add marker, get markers, and duplicate.
"""

from __future__ import annotations

import json

import pytest
from fastmcp import Client


# ---------------------------------------------------------------------------
# Current timeline
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_current(mcp_server: Client) -> None:
    """timeline_get_current returns a dict with timeline info."""
    result = await mcp_server.call_tool("timeline_get_current", {})
    data = result.data
    assert isinstance(data, dict)
    assert data["name"] == "Timeline 1"
    assert data["start_frame"] == 0
    assert data["end_frame"] == 1000
    assert data["video_tracks"] == 3
    assert data["audio_tracks"] == 3
    assert data["start_timecode"] == "01:00:00:00"


@pytest.mark.asyncio
async def test_set_current(mcp_server: Client) -> None:
    """timeline_set_current activates a timeline by name and returns True."""
    # MockProject has 2 timelines ("Timeline 1" and "Timeline 2")
    result = await mcp_server.call_tool(
        "timeline_set_current", {"name": "Timeline 1"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_get_count(mcp_server: Client) -> None:
    """timeline_get_count returns the number of timelines in the project."""
    result = await mcp_server.call_tool("timeline_get_count", {})
    # MockProject.GetTimelineCount() returns 2
    assert result.data == 2


# ---------------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_name(mcp_server: Client) -> None:
    """timeline_get_name returns the name of the current timeline."""
    result = await mcp_server.call_tool("timeline_get_name", {})
    assert result.data == "Timeline 1"


@pytest.mark.asyncio
async def test_set_name(mcp_server: Client) -> None:
    """timeline_set_name renames the current timeline and returns True."""
    result = await mcp_server.call_tool(
        "timeline_set_name", {"name": "Renamed TL"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Tracks
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_track_count(mcp_server: Client) -> None:
    """timeline_get_track_count returns track count for a given type."""
    result = await mcp_server.call_tool(
        "timeline_get_track_count", {"track_type": "video"}
    )
    # MockTimeline.GetTrackCount() always returns 3
    assert result.data == 3


@pytest.mark.asyncio
async def test_add_track(mcp_server: Client) -> None:
    """timeline_add_track adds a track and returns True."""
    result = await mcp_server.call_tool(
        "timeline_add_track", {"track_type": "audio"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Items (clips on tracks)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_items_pagination(mcp_server: Client) -> None:
    """timeline_get_items_in_track returns paginated items for a track."""
    result = await mcp_server.call_tool(
        "timeline_get_items_in_track",
        {"track_type": "video", "track_index": 1, "offset": 0, "limit": 50},
    )
    data = result.data
    assert isinstance(data, dict)
    # MockTimeline.GetItemListInTrack() returns 2 items
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Clip A"
    assert data["items"][1]["name"] == "Clip B"
    assert data["has_more"] is False


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_marker(mcp_server: Client) -> None:
    """timeline_add_marker places a marker on the current timeline."""
    result = await mcp_server.call_tool(
        "timeline_add_marker",
        {"frame_id": 500, "color": "Blue", "name": "Marker1"},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_get_markers(mcp_server: Client) -> None:
    """timeline_get_markers returns markers dict (empty in mock)."""
    result = await mcp_server.call_tool("timeline_get_markers", {})
    # MockTimeline.GetMarkers() returns {} — FastMCP serializes empty dicts
    # as text '{}' but .data may be None; parse from content for reliability
    text = result.content[0].text if result.content else "null"
    data = json.loads(text)
    assert data == {}


# ---------------------------------------------------------------------------
# Duplicate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_duplicate(mcp_server: Client) -> None:
    """timeline_duplicate creates a copy of the current timeline."""
    result = await mcp_server.call_tool("timeline_duplicate", {})
    # MockTimeline.DuplicateTimeline() returns MockTimeline("Timeline 1 copy")
    assert result.data == "Timeline 1 copy"
