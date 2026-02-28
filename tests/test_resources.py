"""Tests for MCP resource modules: system_info, project_info, timeline_info."""

from __future__ import annotations

import json

import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_system_info_resource(mcp_server: Client):
    """resolve://system returns version, product, and current page."""
    result = await mcp_server.read_resource("resolve://system")
    # read_resource returns a list of TextResourceContents
    data = json.loads(result[0].text)
    assert data["version"] == "19.1.2"
    assert data["product"] == "DaVinci Resolve Studio"
    assert data["current_page"] == "edit"


@pytest.mark.asyncio
async def test_project_info_resource(mcp_server: Client):
    """resolve://project returns project name, timeline count, resolution, fps."""
    result = await mcp_server.read_resource("resolve://project")
    data = json.loads(result[0].text)
    assert data["name"] == "Test Project"
    assert data["timeline_count"] == 2
    assert "1920" in data["resolution"]
    assert data["frame_rate"] == "24"


@pytest.mark.asyncio
async def test_timeline_info_resource(mcp_server: Client):
    """resolve://timeline returns timeline name, frame range, track counts."""
    result = await mcp_server.read_resource("resolve://timeline")
    data = json.loads(result[0].text)
    assert data["name"] == "Timeline 1"
    assert data["start_frame"] == 0
    assert data["end_frame"] == 1000
    assert data["video_tracks"] == 3
    assert data["audio_tracks"] == 3
    assert data["start_timecode"] == "01:00:00:00"
    assert data["current_timecode"] == "01:00:00:00"
