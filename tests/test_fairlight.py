"""Tests for Fairlight audio tools.

Covers all 3 tools registered by ``davinci_resolve_mcp.tools.fairlight``:
insert audio, list presets, and apply preset.
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ---------------------------------------------------------------------------
# Insert audio
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_insert_audio(mcp_server: Client) -> None:
    """fairlight_insert_audio imports and appends an audio file."""
    result = await mcp_server.call_tool(
        "fairlight_insert_audio",
        {"file_path": "/audio/voiceover.wav", "track_index": 1},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_insert_audio_default_track(mcp_server: Client) -> None:
    """fairlight_insert_audio uses track_index=1 by default."""
    result = await mcp_server.call_tool(
        "fairlight_insert_audio",
        {"file_path": "/audio/music.mp3"},
    )
    assert result.data is True


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_presets(mcp_server: Client) -> None:
    """fairlight_get_presets returns a list of preset name strings."""
    result = await mcp_server.call_tool("fairlight_get_presets", {})
    data = extract_data(result)
    # MockProject.GetFairlightPresetList() returns ["Dialogue", "Music", "SFX"]
    assert data == ["Dialogue", "Music", "SFX"]


@pytest.mark.asyncio
async def test_apply_preset(mcp_server: Client) -> None:
    """fairlight_apply_preset applies a preset and returns True."""
    result = await mcp_server.call_tool(
        "fairlight_apply_preset",
        {"preset_name": "Dialogue", "track_index": 1},
    )
    assert result.data is True


@pytest.mark.asyncio
async def test_apply_preset_default_track(mcp_server: Client) -> None:
    """fairlight_apply_preset uses track_index=1 by default."""
    result = await mcp_server.call_tool(
        "fairlight_apply_preset",
        {"preset_name": "Music"},
    )
    assert result.data is True
