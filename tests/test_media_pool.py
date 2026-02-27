"""Tests for media pool tools.

Covers 8 key tools registered by ``davinci_resolve_mcp.tools.media_pool``:
root folder, current folder, create folder, clips (paginated), subfolders,
import media, create timeline, create timeline from clips.
"""

from __future__ import annotations

import pytest
from fastmcp import Client


# ---------------------------------------------------------------------------
# Folder navigation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_root_folder(mcp_server: Client) -> None:
    """media_pool_get_root_folder returns the root folder name."""
    result = await mcp_server.call_tool("media_pool_get_root_folder", {})
    # MockMediaPool.GetRootFolder() returns MockFolder("Master")
    assert result.data == "Master"


@pytest.mark.asyncio
async def test_get_current_folder(mcp_server: Client) -> None:
    """media_pool_get_current_folder returns the active folder name."""
    result = await mcp_server.call_tool("media_pool_get_current_folder", {})
    # MockMediaPool.GetCurrentFolder() returns MockFolder("Rushes")
    assert result.data == "Rushes"


@pytest.mark.asyncio
async def test_create_folder(mcp_server: Client) -> None:
    """media_pool_create_folder creates a subfolder and returns True."""
    result = await mcp_server.call_tool(
        "media_pool_create_folder", {"name": "NewFolder"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_clips_pagination(mcp_server: Client) -> None:
    """media_pool_get_clips returns paginated clip info from the current folder."""
    result = await mcp_server.call_tool(
        "media_pool_get_clips", {"offset": 0, "limit": 10}
    )
    data = result.data
    assert isinstance(data, dict)
    # MockFolder.GetClipList() returns 2 clips
    assert data["total"] == 2
    assert data["offset"] == 0
    assert data["limit"] == 10
    assert data["has_more"] is False
    assert len(data["items"]) == 2
    # Verify clip structure
    first = data["items"][0]
    assert first["name"] == "clip01"
    assert first["fps"] == "24"


@pytest.mark.asyncio
async def test_get_subfolders(mcp_server: Client) -> None:
    """media_pool_get_subfolders lists subfolder names."""
    result = await mcp_server.call_tool("media_pool_get_subfolders", {})
    # MockFolder.GetSubFolderList() returns [MockFolder("Sub")]
    assert result.data == ["Sub"]


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_import_media(mcp_server: Client) -> None:
    """media_pool_import_media imports files and returns imported clip names."""
    result = await mcp_server.call_tool(
        "media_pool_import_media",
        {"file_paths": ["/media/clip01.mov", "/media/clip02.mov"]},
    )
    # MockMediaPool.ImportMedia() returns [MockMediaPoolItem("imported_clip")]
    assert result.data == ["imported_clip"]


# ---------------------------------------------------------------------------
# Timeline creation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_timeline(mcp_server: Client) -> None:
    """media_pool_create_timeline creates an empty timeline and returns its name."""
    result = await mcp_server.call_tool(
        "media_pool_create_timeline", {"name": "My Timeline"}
    )
    assert result.data == "My Timeline"


@pytest.mark.asyncio
async def test_create_timeline_from_clips(mcp_server: Client) -> None:
    """media_pool_create_timeline_from_clips creates a timeline populated with clips."""
    result = await mcp_server.call_tool(
        "media_pool_create_timeline_from_clips",
        {"name": "Edited TL", "clip_names": ["clip01", "clip02"]},
    )
    assert result.data == "Edited TL"
