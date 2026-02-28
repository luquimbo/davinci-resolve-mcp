"""Tests for Gallery tools.

Covers all 14 tools registered by ``davinci_resolve_mcp.tools.gallery``:
list albums, get current album, set current album, create album, delete
album (destructiveHint), list stills, grab still, import stills, export
stills, delete stills (destructiveHint), apply grade from still, list
PowerGrade albums, list PowerGrade stills, and set current PowerGrade album.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ---------------------------------------------------------------------------
# Album management
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_albums(mcp_server: Client) -> None:
    """gallery_get_albums returns a list of still album names."""
    result = await mcp_server.call_tool("gallery_get_albums", {})
    data = extract_data(result)
    # MockGallery.GetGalleryStillAlbums() returns [MockAlbum("Stills 1")]
    assert data == ["Stills 1"]


@pytest.mark.asyncio
async def test_get_current_album(mcp_server: Client) -> None:
    """gallery_get_current_album returns the name of the active album."""
    result = await mcp_server.call_tool("gallery_get_current_album", {})
    # MockGallery.GetCurrentStillAlbum() returns MockAlbum("Stills 1")
    assert result.data == "Stills 1"


@pytest.mark.asyncio
async def test_set_current_album(mcp_server: Client) -> None:
    """gallery_set_current_album switches the active album and returns True."""
    result = await mcp_server.call_tool(
        "gallery_set_current_album", {"album_name": "Stills 1"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_set_current_album_not_found(mcp_server: Client) -> None:
    """gallery_set_current_album raises when the album does not exist."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_set_current_album", {"album_name": "Does Not Exist"}
        )


@pytest.mark.asyncio
async def test_create_album(mcp_server: Client) -> None:
    """gallery_create_album creates a new still album and returns True."""
    result = await mcp_server.call_tool(
        "gallery_create_album", {"name": "Hero Looks"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_album(mcp_server: Client) -> None:
    """gallery_delete_album deletes a still album (destructiveHint)."""
    result = await mcp_server.call_tool(
        "gallery_delete_album", {"album_name": "Stills 1"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_album_not_found(mcp_server: Client) -> None:
    """gallery_delete_album raises when the album does not exist."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_delete_album", {"album_name": "Ghost Album"}
        )


# ---------------------------------------------------------------------------
# Stills
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_stills_default_album(mcp_server: Client) -> None:
    """gallery_get_stills with no album_name uses the current album."""
    result = await mcp_server.call_tool("gallery_get_stills", {})
    data = extract_data(result)
    # MockAlbum.GetStills() returns [MockStill()] whose GetLabel() -> "Still 1"
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["index"] == 0
    assert data[0]["name"] == "Still 1"


@pytest.mark.asyncio
async def test_get_stills_named_album(mcp_server: Client) -> None:
    """gallery_get_stills with an explicit album name."""
    result = await mcp_server.call_tool(
        "gallery_get_stills", {"album_name": "Stills 1"}
    )
    data = extract_data(result)
    assert len(data) == 1
    assert data[0]["name"] == "Still 1"


@pytest.mark.asyncio
async def test_grab_still(mcp_server: Client) -> None:
    """gallery_grab_still captures a snapshot and returns True."""
    result = await mcp_server.call_tool("gallery_grab_still", {})
    # MockTimeline.GrabStill() returns True (first approach tried)
    assert result.data is True


@pytest.mark.asyncio
async def test_import_stills(mcp_server: Client) -> None:
    """gallery_import_stills imports image files into an album."""
    result = await mcp_server.call_tool(
        "gallery_import_stills",
        {"file_paths": ["/stills/frame001.dpx", "/stills/frame002.dpx"]},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_import_stills_named_album(mcp_server: Client) -> None:
    """gallery_import_stills into a specific album by name."""
    result = await mcp_server.call_tool(
        "gallery_import_stills",
        {
            "file_paths": ["/stills/frame001.dpx"],
            "album_name": "Stills 1",
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_export_stills(mcp_server: Client) -> None:
    """gallery_export_stills exports selected stills to disk."""
    result = await mcp_server.call_tool(
        "gallery_export_stills",
        {"still_indices": [0], "export_path": "/tmp/stills_export"},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_export_stills_invalid_index(mcp_server: Client) -> None:
    """gallery_export_stills raises when all indices are out of range."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_export_stills",
            {"still_indices": [99], "export_path": "/tmp/stills_export"},
        )


@pytest.mark.asyncio
async def test_delete_stills(mcp_server: Client) -> None:
    """gallery_delete_stills removes selected stills (destructiveHint)."""
    result = await mcp_server.call_tool(
        "gallery_delete_stills",
        {"still_indices": [0]},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_stills_invalid_index(mcp_server: Client) -> None:
    """gallery_delete_stills raises when all indices are out of range."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_delete_stills",
            {"still_indices": [50]},
        )


# ---------------------------------------------------------------------------
# Apply grade from gallery still
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_apply_grade_from_still(mcp_server: Client) -> None:
    """gallery_apply_grade_from_still applies a grade to timeline items."""
    result = await mcp_server.call_tool(
        "gallery_apply_grade_from_still",
        {
            "still_index": 0,
            "item_names": ["Clip A"],
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_apply_grade_from_still_multiple(mcp_server: Client) -> None:
    """gallery_apply_grade_from_still applies to multiple items."""
    result = await mcp_server.call_tool(
        "gallery_apply_grade_from_still",
        {
            "still_index": 0,
            "item_names": ["Clip A", "Clip B"],
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_apply_grade_from_still_out_of_range(mcp_server: Client) -> None:
    """gallery_apply_grade_from_still raises when still_index is out of range."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_apply_grade_from_still",
            {
                "still_index": 99,
                "item_names": ["Clip A"],
                "track_type": "video",
                "track_index": 1,
            },
        )


# ---------------------------------------------------------------------------
# PowerGrade albums
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_powergrade_albums(mcp_server: Client) -> None:
    """gallery_get_powergrade_albums returns PowerGrade album names."""
    result = await mcp_server.call_tool("gallery_get_powergrade_albums", {})
    data = extract_data(result)
    # MockGallery.GetGalleryPowerGradeAlbums() returns [MockAlbum("PowerGrade 1")]
    assert data == ["PowerGrade 1"]


@pytest.mark.asyncio
async def test_get_powergrade_stills(mcp_server: Client) -> None:
    """gallery_get_powergrade_stills lists stills in a PowerGrade album."""
    result = await mcp_server.call_tool(
        "gallery_get_powergrade_stills", {"album_name": "PowerGrade 1"}
    )
    data = extract_data(result)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["index"] == 0
    assert data[0]["name"] == "Still 1"


@pytest.mark.asyncio
async def test_get_powergrade_stills_not_found(mcp_server: Client) -> None:
    """gallery_get_powergrade_stills raises when the album does not exist."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_get_powergrade_stills", {"album_name": "NoSuchGrade"}
        )


@pytest.mark.asyncio
async def test_set_current_powergrade_album(mcp_server: Client) -> None:
    """gallery_set_current_powergrade_album switches the active PG album."""
    result = await mcp_server.call_tool(
        "gallery_set_current_powergrade_album", {"album_name": "PowerGrade 1"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_set_current_powergrade_album_not_found(mcp_server: Client) -> None:
    """gallery_set_current_powergrade_album raises for a missing album."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "gallery_set_current_powergrade_album", {"album_name": "Phantom"}
        )
