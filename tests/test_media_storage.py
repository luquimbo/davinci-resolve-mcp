"""Tests for all 4 media-storage tools in media_storage.py.

Covers storage_get_volumes, storage_get_subfolders, storage_get_files,
and storage_import_to_pool with happy-path assertions.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ===================================================================
# storage_get_volumes
# ===================================================================

@pytest.mark.asyncio
async def test_storage_get_volumes(mcp_server: Client):
    """storage_get_volumes returns the list of mounted volumes."""
    result = await mcp_server.call_tool("storage_get_volumes", {})
    data = extract_data(result)
    assert isinstance(data, list)
    assert "/Volumes/Media" in data


# ===================================================================
# storage_get_subfolders
# ===================================================================

@pytest.mark.asyncio
async def test_storage_get_subfolders(mcp_server: Client):
    """storage_get_subfolders returns subfolders for a given volume path."""
    result = await mcp_server.call_tool("storage_get_subfolders", {
        "volume_path": "/Volumes/Media",
    })
    data = extract_data(result)
    assert isinstance(data, list)
    assert "Footage" in data
    assert "Audio" in data


# ===================================================================
# storage_get_files
# ===================================================================

@pytest.mark.asyncio
async def test_storage_get_files(mcp_server: Client):
    """storage_get_files returns media files in a folder."""
    result = await mcp_server.call_tool("storage_get_files", {
        "folder_path": "/Volumes/Media/Footage",
    })
    data = extract_data(result)
    assert isinstance(data, list)
    assert "clip01.mov" in data
    assert "clip02.mp4" in data


# ===================================================================
# storage_import_to_pool
# ===================================================================

@pytest.mark.asyncio
async def test_storage_import_to_pool(mcp_server: Client):
    """storage_import_to_pool imports files and returns clip names."""
    result = await mcp_server.call_tool("storage_import_to_pool", {
        "file_paths": ["/Volumes/Media/Footage/clip01.mov"],
    })
    data = extract_data(result)
    assert isinstance(data, list)
    assert len(data) >= 1
    # MockMediaStorage.AddItemListToMediaPool returns MockMediaPoolItem("clip01")
    assert "clip01" in data
