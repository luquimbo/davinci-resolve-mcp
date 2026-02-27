"""Tests for render / Deliver-page tools.

Covers 9 key tools registered by ``davinci_resolve_mcp.tools.render``:
get formats, get codecs, get presets, load preset, set format+codec,
add job, get jobs, start render, get status.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ---------------------------------------------------------------------------
# Formats & codecs
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_formats(mcp_server: Client) -> None:
    """render_get_formats returns available render formats."""
    result = await mcp_server.call_tool("render_get_formats", {})
    data = result.data
    assert isinstance(data, dict)
    assert "mp4" in data
    assert "mov" in data


@pytest.mark.asyncio
async def test_get_codecs(mcp_server: Client) -> None:
    """render_get_codecs returns codecs for a given format."""
    result = await mcp_server.call_tool(
        "render_get_codecs", {"format_name": "mp4"}
    )
    data = result.data
    assert isinstance(data, dict)
    assert "H.264" in data
    assert "H.265" in data


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_presets(mcp_server: Client) -> None:
    """render_get_presets lists saved render preset names."""
    result = await mcp_server.call_tool("render_get_presets", {})
    assert "YouTube 1080p" in result.data
    assert "ProRes Master" in result.data


@pytest.mark.asyncio
async def test_load_preset(mcp_server: Client) -> None:
    """render_load_preset applies a preset and returns True."""
    result = await mcp_server.call_tool(
        "render_load_preset", {"preset_name": "YouTube 1080p"}
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Format & codec selection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_set_format_and_codec(mcp_server: Client) -> None:
    """render_set_format_and_codec sets the active format+codec."""
    result = await mcp_server.call_tool(
        "render_set_format_and_codec",
        {"format_name": "QuickTime", "codec_name": "H.265"},
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Job queue
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_job(mcp_server: Client) -> None:
    """render_add_job queues a render job and returns the job ID."""
    result = await mcp_server.call_tool("render_add_job", {})
    # MockProject.AddRenderJob() returns "job-001"
    assert result.data == "job-001"


@pytest.mark.asyncio
async def test_get_jobs(mcp_server: Client) -> None:
    """render_get_jobs lists queued render jobs with normalised keys."""
    result = await mcp_server.call_tool("render_get_jobs", {})
    # render_get_jobs returns list[dict] — use extract_data to handle
    # FastMCP's opaque wrapper objects for inner dicts
    data = extract_data(result)
    assert isinstance(data, list)
    assert len(data) == 1
    job = data[0]
    assert job["job_id"] == "job-001"
    assert job["status"] == "Ready"
    assert job["timeline_name"] == "Timeline 1"
    assert job["target_dir"] == "/tmp"
    assert job["output_filename"] == "out.mp4"


# ---------------------------------------------------------------------------
# Render execution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_render(mcp_server: Client) -> None:
    """render_start begins rendering and returns True."""
    result = await mcp_server.call_tool("render_start", {})
    assert result.data is True


@pytest.mark.asyncio
async def test_get_status(mcp_server: Client) -> None:
    """render_get_status returns progress info for a specific job."""
    result = await mcp_server.call_tool(
        "render_get_status", {"job_id": "job-001"}
    )
    data = result.data
    assert isinstance(data, dict)
    assert data["job_id"] == "job-001"
    assert data["status"] == "Complete"
    assert data["progress"] == 100
