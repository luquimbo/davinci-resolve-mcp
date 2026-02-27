"""Tests for timeline item tools.

Covers 8 key tools registered by ``davinci_resolve_mcp.tools.timeline_item``:
get name, duration, start/end, set transform, set crop, set composite,
get color, and set enabled.
"""

from __future__ import annotations

import pytest
from fastmcp import Client


# ---------------------------------------------------------------------------
# Basic info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_name(mcp_server: Client) -> None:
    """item_get_name returns the display name of a timeline item."""
    result = await mcp_server.call_tool(
        "item_get_name",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    assert result.data == "Clip A"


@pytest.mark.asyncio
async def test_get_duration(mcp_server: Client) -> None:
    """item_get_duration returns the item's duration in frames."""
    result = await mcp_server.call_tool(
        "item_get_duration",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetDuration() returns 100
    assert result.data == 100


@pytest.mark.asyncio
async def test_get_start_end(mcp_server: Client) -> None:
    """item_get_start_end returns start, end, and duration."""
    result = await mcp_server.call_tool(
        "item_get_start_end",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    data = result.data
    assert isinstance(data, dict)
    assert data["start"] == 0
    assert data["end"] == 100
    assert data["duration"] == 100


# ---------------------------------------------------------------------------
# Transform, crop, composite
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_transform(mcp_server: Client) -> None:
    """item_set_transform applies zoom/position/rotation and returns True."""
    result = await mcp_server.call_tool(
        "item_set_transform",
        {
            "item_name": "Clip A",
            "zoom_x": 1.5,
            "position_x": 100.0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_set_crop(mcp_server: Client) -> None:
    """item_set_crop applies crop values and returns True."""
    result = await mcp_server.call_tool(
        "item_set_crop",
        {
            "item_name": "Clip A",
            "left": 10.0,
            "right": 10.0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_set_composite(mcp_server: Client) -> None:
    """item_set_composite sets blend mode and opacity."""
    result = await mcp_server.call_tool(
        "item_set_composite",
        {
            "item_name": "Clip A",
            "mode": "Multiply",
            "opacity": 75.0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Color label
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_color(mcp_server: Client) -> None:
    """item_get_color returns the clip color label (empty for mock)."""
    result = await mcp_server.call_tool(
        "item_get_color",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetClipColor() returns ""
    assert result.data == ""


# ---------------------------------------------------------------------------
# Enable/disable
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_enabled(mcp_server: Client) -> None:
    """item_set_enabled enables or disables a timeline item."""
    result = await mcp_server.call_tool(
        "item_set_enabled",
        {
            "item_name": "Clip A",
            "enabled": False,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True
