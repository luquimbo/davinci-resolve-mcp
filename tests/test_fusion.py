"""Tests for Fusion composition tools.

Covers all 11 tools registered by ``davinci_resolve_mcp.tools.fusion``:
comp count, comp names, comp info, add comp, import comp, export comp,
delete comp (destructiveHint), rename comp, insert generator, insert title,
and tool list within a composition.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ---------------------------------------------------------------------------
# Composition queries
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_comp_count(mcp_server: Client) -> None:
    """fusion_get_comp_count returns the number of Fusion comps on an item."""
    result = await mcp_server.call_tool(
        "fusion_get_comp_count",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    # MockTimelineItem.GetFusionCompCount() returns 1
    assert result.data == 1


@pytest.mark.asyncio
async def test_get_comp_names(mcp_server: Client) -> None:
    """fusion_get_comp_names returns a list of composition name strings."""
    result = await mcp_server.call_tool(
        "fusion_get_comp_names",
        {"item_name": "Clip A", "track_type": "video", "track_index": 1},
    )
    data = extract_data(result)
    # MockTimelineItem.GetFusionCompNameList() returns ["Comp 1"]
    assert data == ["Comp 1"]


@pytest.mark.asyncio
async def test_get_comp(mcp_server: Client) -> None:
    """fusion_get_comp returns a dict with name and tool_count."""
    result = await mcp_server.call_tool(
        "fusion_get_comp",
        {
            "item_name": "Clip A",
            "comp_name": "Comp 1",
            "track_type": "video",
            "track_index": 1,
        },
    )
    data = result.data
    assert isinstance(data, dict)
    assert data["name"] == "Comp 1"
    # MockFusionComp.GetToolList() returns {"tool1": MockFusionTool()}, so tool_count = 1
    assert data["tool_count"] == 1


@pytest.mark.asyncio
async def test_get_comp_item_not_found(mcp_server: Client) -> None:
    """fusion_get_comp_count raises when the item is not on the track."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "fusion_get_comp_count",
            {"item_name": "NonExistent", "track_type": "video", "track_index": 1},
        )


# ---------------------------------------------------------------------------
# Composition CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_comp(mcp_server: Client) -> None:
    """fusion_add_comp adds a new Fusion comp to the playhead item."""
    result = await mcp_server.call_tool("fusion_add_comp", {})
    # MockTimelineItem.AddFusionComp() returns True
    assert result.data is True


@pytest.mark.asyncio
async def test_import_comp(mcp_server: Client) -> None:
    """fusion_import_comp imports a .comp file onto a timeline item."""
    result = await mcp_server.call_tool(
        "fusion_import_comp",
        {
            "item_name": "Clip A",
            "comp_path": "/comps/title_template.comp",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_export_comp(mcp_server: Client) -> None:
    """fusion_export_comp exports a composition to a .comp file."""
    result = await mcp_server.call_tool(
        "fusion_export_comp",
        {
            "item_name": "Clip A",
            "comp_name": "Comp 1",
            "export_path": "/tmp/exported.comp",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_delete_comp(mcp_server: Client) -> None:
    """fusion_delete_comp deletes a composition by name (destructiveHint)."""
    result = await mcp_server.call_tool(
        "fusion_delete_comp",
        {
            "item_name": "Clip A",
            "comp_name": "Comp 1",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_rename_comp(mcp_server: Client) -> None:
    """fusion_rename_comp renames a composition in-place."""
    result = await mcp_server.call_tool(
        "fusion_rename_comp",
        {
            "item_name": "Clip A",
            "old_name": "Comp 1",
            "new_name": "Hero Title",
            "track_type": "video",
            "track_index": 1,
        },
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Insert generators and titles
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insert_generator(mcp_server: Client) -> None:
    """fusion_insert_generator appends a Fusion generator to the timeline."""
    result = await mcp_server.call_tool(
        "fusion_insert_generator",
        {"generator_name": "Fusion Composition"},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_insert_title(mcp_server: Client) -> None:
    """fusion_insert_title appends a Fusion title to the timeline."""
    result = await mcp_server.call_tool(
        "fusion_insert_title",
        {"title_name": "Text+"},
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Tool listing within a composition
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_tool_list(mcp_server: Client) -> None:
    """fusion_get_tool_list returns tool names inside a composition."""
    result = await mcp_server.call_tool(
        "fusion_get_tool_list",
        {
            "item_name": "Clip A",
            "comp_name": "Comp 1",
            "track_type": "video",
            "track_index": 1,
        },
    )
    data = extract_data(result)
    # MockFusionComp.GetToolList() returns {"tool1": MockFusionTool()},
    # MockFusionTool.GetAttrs("TOOLS_Name") returns "Background1"
    assert data == ["Background1"]


# ---------------------------------------------------------------------------
# Track type validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_track_type(mcp_server: Client) -> None:
    """Fusion tools raise for an invalid track_type value."""
    with pytest.raises(Exception):
        await mcp_server.call_tool(
            "fusion_get_comp_count",
            {"item_name": "Clip A", "track_type": "bogus", "track_index": 1},
        )
