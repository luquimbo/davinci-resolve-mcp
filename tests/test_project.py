"""Tests for project management tools.

Covers all 13 tools registered by ``davinci_resolve_mcp.tools.project``:
list, create (success + failure), open, save, close, delete, get_current,
get_setting, set_setting, import, export, folder_list, folder_open.
"""

from __future__ import annotations

import pytest
from fastmcp import Client


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list(mcp_server: Client) -> None:
    """project_list returns names of projects in the current DB folder."""
    result = await mcp_server.call_tool("project_list", {})
    assert result.data == ["Project A", "Project B"]


@pytest.mark.asyncio
async def test_create(mcp_server: Client) -> None:
    """project_create returns the name of the newly created project."""
    result = await mcp_server.call_tool("project_create", {"name": "New Project"})
    # MockProject.GetName() returns "Test Project" (the mock always uses that)
    assert result.data == "Test Project"


@pytest.mark.asyncio
async def test_create_fails(mcp_server: Client) -> None:
    """project_create raises when project name already exists (mock returns None for 'Existing')."""
    with pytest.raises(Exception):
        await mcp_server.call_tool("project_create", {"name": "Existing"})


@pytest.mark.asyncio
async def test_open(mcp_server: Client) -> None:
    """project_open loads an existing project and returns True."""
    result = await mcp_server.call_tool("project_open", {"name": "Project A"})
    assert result.data is True


@pytest.mark.asyncio
async def test_save(mcp_server: Client) -> None:
    """project_save saves the current project and returns True."""
    result = await mcp_server.call_tool("project_save", {})
    assert result.data is True


@pytest.mark.asyncio
async def test_close(mcp_server: Client) -> None:
    """project_close closes the current project and returns True."""
    result = await mcp_server.call_tool("project_close", {})
    assert result.data is True


@pytest.mark.asyncio
async def test_delete(mcp_server: Client) -> None:
    """project_delete removes a project and returns True."""
    result = await mcp_server.call_tool("project_delete", {"name": "Project B"})
    assert result.data is True


# ---------------------------------------------------------------------------
# Current project info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_current(mcp_server: Client) -> None:
    """project_get_current returns name and timeline count for the open project."""
    result = await mcp_server.call_tool("project_get_current", {})
    data = result.data
    assert isinstance(data, dict)
    assert data["name"] == "Test Project"
    assert data["timeline_count"] == 2


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_setting(mcp_server: Client) -> None:
    """project_get_setting returns the value for a given setting key."""
    result = await mcp_server.call_tool(
        "project_get_setting", {"key": "timelineResolutionWidth"}
    )
    # MockProject.GetSetting() returns "1920" when "Width" is in the key
    assert result.data == "1920"


@pytest.mark.asyncio
async def test_set_setting(mcp_server: Client) -> None:
    """project_set_setting applies a setting and returns True."""
    result = await mcp_server.call_tool(
        "project_set_setting", {"key": "timelineFrameRate", "value": "30"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_import(mcp_server: Client) -> None:
    """project_import imports a .drp file and returns True."""
    result = await mcp_server.call_tool(
        "project_import", {"file_path": "/tmp/project.drp"}
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_export(mcp_server: Client) -> None:
    """project_export exports the current project to a .drp file."""
    result = await mcp_server.call_tool(
        "project_export", {"file_path": "/tmp/export.drp"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Database folder navigation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_folder_list(mcp_server: Client) -> None:
    """project_folder_list returns sub-folder names."""
    result = await mcp_server.call_tool("project_folder_list", {})
    assert result.data == ["Folder1"]


@pytest.mark.asyncio
async def test_folder_open(mcp_server: Client) -> None:
    """project_folder_open navigates into a sub-folder and returns True."""
    result = await mcp_server.call_tool(
        "project_folder_open", {"folder_name": "Folder1"}
    )
    assert result.data is True
