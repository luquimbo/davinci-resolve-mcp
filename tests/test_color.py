"""Tests for color grading tools.

Covers all 22 tools registered by ``davinci_resolve_mcp.tools.color``:
node info, LUT operations, CDL get/set, node enable, DRX grade application,
grade reset, grade version management (add, count, list, set current, get
current, delete, rename, load), and color group operations (list, create,
delete, assign, remove).
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ---------------------------------------------------------------------------
# Node information
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_num_nodes(mcp_server: Client) -> None:
    """color_get_num_nodes returns the node count for a timeline item."""
    result = await mcp_server.call_tool(
        "color_get_num_nodes",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetNumNodes() returns 3
    assert result.data == 3


@pytest.mark.asyncio
async def test_get_num_nodes_item_not_found(mcp_server: Client) -> None:
    """color_get_num_nodes raises when the item is not on the track."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "color_get_num_nodes",
            {"item_name": "NonExistent", "track_type": "video", "track_index": 1},
        )


# ---------------------------------------------------------------------------
# LUT operations
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_lut(mcp_server: Client) -> None:
    """color_set_lut applies a LUT file to a node and returns True."""
    result = await mcp_server.call_tool(
        "color_set_lut",
        {
            "item_name": "Clip A",
            "node_index": 1,
            "lut_path": "/path/to/my.cube",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_get_lut(mcp_server: Client) -> None:
    """color_get_lut returns the LUT path assigned to a node."""
    result = await mcp_server.call_tool(
        "color_get_lut",
        {
            "item_name": "Clip A",
            "node_index": 1,
            "track_type": "video",
            "track_index": 1,
        },
    )
    # MockTimelineItem.GetLUT() returns "/path/to/lut.cube"
    assert result.data == "/path/to/lut.cube"


@pytest.mark.asyncio
async def test_export_lut(mcp_server: Client) -> None:
    """color_export_lut exports the grade as a LUT file and returns True."""
    result = await mcp_server.call_tool(
        "color_export_lut",
        {
            "item_name": "Clip A",
            "lut_type": "3D LUT (33 Point)",
            "export_path": "/tmp/export.cube",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# CDL
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_cdl(mcp_server: Client) -> None:
    """color_get_cdl returns a dict with Slope, Offset, Power, Saturation."""
    result = await mcp_server.call_tool(
        "color_get_cdl",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    data = result.data
    assert isinstance(data, dict)
    assert data["Slope"] == [1, 1, 1]
    assert data["Offset"] == [0, 0, 0]
    assert data["Power"] == [1, 1, 1]
    assert data["Saturation"] == 1.0


@pytest.mark.asyncio
async def test_set_cdl(mcp_server: Client) -> None:
    """color_set_cdl applies CDL values and returns True."""
    result = await mcp_server.call_tool(
        "color_set_cdl",
        {
            "item_name": "Clip A",
            "cdl": {
                "Slope": [1.1, 1.0, 0.9],
                "Offset": [0.01, 0.0, -0.01],
                "Power": [1.0, 1.0, 1.0],
                "Saturation": 1.2,
            },
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_set_cdl_invalid_slope(mcp_server: Client) -> None:
    """color_set_cdl raises when Slope has wrong number of elements."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "color_set_cdl",
            {
                "item_name": "Clip A",
                "cdl": {
                    "Slope": [1.0, 1.0],  # Only 2 values instead of 3
                    "Offset": [0.0, 0.0, 0.0],
                    "Power": [1.0, 1.0, 1.0],
                    "Saturation": 1.0,
                },
                "track_type": "video",
                "track_index": 1,
            },
        )


# ---------------------------------------------------------------------------
# Node enable/disable
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_node_enabled(mcp_server: Client) -> None:
    """color_set_node_enabled toggles a node and returns True."""
    result = await mcp_server.call_tool(
        "color_set_node_enabled",
        {
            "item_name": "Clip A",
            "node_index": 1,
            "enabled": False,
            "track_type": "video",
            "track_index": 1,
        },
    )
    # MockTimelineItem.SetNodeEnabled() returns True
    assert result.data is True


@pytest.mark.asyncio
async def test_set_node_enabled_enable(mcp_server: Client) -> None:
    """color_set_node_enabled can also enable a node."""
    result = await mcp_server.call_tool(
        "color_set_node_enabled",
        {
            "item_name": "Clip A",
            "node_index": 2,
            "enabled": True,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Grade application from DRX
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_apply_drx(mcp_server: Client) -> None:
    """color_apply_drx applies a .drx grade file and returns True."""
    result = await mcp_server.call_tool(
        "color_apply_drx",
        {
            "drx_path": "/grades/look.drx",
            "grade_mode": 0,
            "item_names": ["Clip A"],
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_apply_drx_multiple_items(mcp_server: Client) -> None:
    """color_apply_drx can apply to multiple items at once."""
    result = await mcp_server.call_tool(
        "color_apply_drx",
        {
            "drx_path": "/grades/look.drx",
            "grade_mode": 1,
            "item_names": ["Clip A", "Clip B"],
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_apply_drx_invalid_grade_mode(mcp_server: Client) -> None:
    """color_apply_drx raises for an invalid grade_mode value."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "color_apply_drx",
            {
                "drx_path": "/grades/look.drx",
                "grade_mode": 5,
                "item_names": ["Clip A"],
                "track_type": "video",
                "track_index": 1,
            },
        )


# ---------------------------------------------------------------------------
# Grade reset (destructiveHint)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reset_grade(mcp_server: Client) -> None:
    """color_reset_grade resets the grade to identity CDL and returns True."""
    result = await mcp_server.call_tool(
        "color_reset_grade",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Grade version management
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_version(mcp_server: Client) -> None:
    """color_add_version creates a new local grade version and returns True."""
    result = await mcp_server.call_tool(
        "color_add_version",
        {
            "item_name": "Clip A",
            "version_name": "Hero Look",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_get_version_count(mcp_server: Client) -> None:
    """color_get_version_count returns the number of grade versions."""
    result = await mcp_server.call_tool(
        "color_get_version_count",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetVersionNameList(0) returns ["Version 1", "Default"]
    assert result.data == 2


@pytest.mark.asyncio
async def test_get_versions(mcp_server: Client) -> None:
    """color_get_versions returns a list of version name strings."""
    result = await mcp_server.call_tool(
        "color_get_versions",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    data = extract_data(result)
    assert data == ["Version 1", "Default"]


@pytest.mark.asyncio
async def test_set_current_version(mcp_server: Client) -> None:
    """color_set_current_version switches the active grade version."""
    result = await mcp_server.call_tool(
        "color_set_current_version",
        {
            "item_name": "Clip A",
            "version_name": "Default",
            "version_type": 0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_get_current_version(mcp_server: Client) -> None:
    """color_get_current_version returns the active version name."""
    result = await mcp_server.call_tool(
        "color_get_current_version",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetCurrentVersion(0) returns {"versionName": "Default"}
    assert result.data == "Default"


@pytest.mark.asyncio
async def test_delete_version(mcp_server: Client) -> None:
    """color_delete_version removes a grade version (destructiveHint)."""
    result = await mcp_server.call_tool(
        "color_delete_version",
        {
            "item_name": "Clip A",
            "version_name": "Version 1",
            "version_type": 0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_rename_version(mcp_server: Client) -> None:
    """color_rename_version renames a grade version and returns True."""
    result = await mcp_server.call_tool(
        "color_rename_version",
        {
            "item_name": "Clip A",
            "old_name": "Version 1",
            "new_name": "Hero Grade",
            "version_type": 0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_load_version(mcp_server: Client) -> None:
    """color_load_version loads a specific version onto the item."""
    result = await mcp_server.call_tool(
        "color_load_version",
        {
            "item_name": "Clip A",
            "version_name": "Default",
            "version_type": 0,
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Color groups (project-level)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_group_list(mcp_server: Client) -> None:
    """color_get_group_list returns color groups from the project."""
    result = await mcp_server.call_tool("color_get_group_list", {})
    data = extract_data(result)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Group 1"
    assert data[0]["id"] == "group-001"


@pytest.mark.asyncio
async def test_create_group(mcp_server: Client) -> None:
    """color_create_group creates a new color group and returns True."""
    result = await mcp_server.call_tool(
        "color_create_group", {"group_name": "Day Ext"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_group(mcp_server: Client) -> None:
    """color_delete_group deletes a color group by ID (destructiveHint)."""
    result = await mcp_server.call_tool(
        "color_delete_group", {"group_id": "group-001"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_assign_to_group(mcp_server: Client) -> None:
    """color_assign_to_group adds a timeline item to a color group."""
    result = await mcp_server.call_tool(
        "color_assign_to_group",
        {
            "item_name": "Clip A",
            "group_id": "group-001",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_remove_from_group(mcp_server: Client) -> None:
    """color_remove_from_group removes a timeline item from a color group."""
    result = await mcp_server.call_tool(
        "color_remove_from_group",
        {
            "item_name": "Clip A",
            "group_id": "group-001",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Track type validation (shared across item-based tools)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_track_type(mcp_server: Client) -> None:
    """Color tools raise for an invalid track_type value."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "color_get_num_nodes",
            {"item_name": "Clip A", "track_type": "invalid", "track_index": 1},
        )
