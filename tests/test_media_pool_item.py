"""Tests for all 21 media-pool clip tools in media_pool_item.py.

Covers happy paths, error paths (empty clip_name, clip not found),
and validation (empty new_name for clip_set_name).
"""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ===================================================================
# Name — clip_get_name, clip_set_name
# ===================================================================

@pytest.mark.asyncio
async def test_clip_get_name(mcp_server: Client):
    """clip_get_name returns the display name of a clip."""
    result = await mcp_server.call_tool("clip_get_name", {"clip_name": "clip01"})
    assert extract_data(result) == "clip01"


@pytest.mark.asyncio
async def test_clip_get_name_clip_not_found(mcp_server: Client):
    """clip_get_name raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_name", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_set_name(mcp_server: Client):
    """clip_set_name renames a clip successfully."""
    result = await mcp_server.call_tool("clip_set_name", {
        "clip_name": "clip01",
        "new_name": "clip01_renamed",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_set_name_empty_new_name(mcp_server: Client):
    """clip_set_name rejects an empty new_name."""
    with pytest.raises(Exception, match="empty"):
        await mcp_server.call_tool("clip_set_name", {
            "clip_name": "clip01",
            "new_name": "",
        })


@pytest.mark.asyncio
async def test_clip_set_name_whitespace_new_name(mcp_server: Client):
    """clip_set_name rejects a whitespace-only new_name."""
    with pytest.raises(Exception, match="empty"):
        await mcp_server.call_tool("clip_set_name", {
            "clip_name": "clip01",
            "new_name": "   ",
        })


@pytest.mark.asyncio
async def test_clip_set_name_clip_not_found(mcp_server: Client):
    """clip_set_name raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_set_name", {
            "clip_name": "nonexistent",
            "new_name": "new_name",
        })


# ===================================================================
# Metadata — clip_get_metadata, clip_set_metadata
# ===================================================================

@pytest.mark.asyncio
async def test_clip_get_metadata(mcp_server: Client):
    """clip_get_metadata returns the metadata dict for a clip."""
    result = await mcp_server.call_tool("clip_get_metadata", {"clip_name": "clip01"})
    data = extract_data(result)
    assert isinstance(data, dict)
    assert data["Reel"] == "A001"


@pytest.mark.asyncio
async def test_clip_get_metadata_clip_not_found(mcp_server: Client):
    """clip_get_metadata raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_metadata", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_set_metadata(mcp_server: Client):
    """clip_set_metadata sets a metadata field on a clip."""
    result = await mcp_server.call_tool("clip_set_metadata", {
        "clip_name": "clip01",
        "key": "Description",
        "value": "Test description",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_set_metadata_clip_not_found(mcp_server: Client):
    """clip_set_metadata raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_set_metadata", {
            "clip_name": "nonexistent",
            "key": "Description",
            "value": "Test",
        })


# ===================================================================
# Properties — clip_get_properties, clip_set_property
# ===================================================================

@pytest.mark.asyncio
async def test_clip_get_properties(mcp_server: Client):
    """clip_get_properties returns the full property dict for a clip."""
    result = await mcp_server.call_tool("clip_get_properties", {"clip_name": "clip01"})
    data = extract_data(result)
    assert isinstance(data, dict)
    assert data["Clip Name"] == "clip01"
    assert data["Duration"] == "00:01:00:00"
    assert data["FPS"] == "24"


@pytest.mark.asyncio
async def test_clip_get_properties_clip_not_found(mcp_server: Client):
    """clip_get_properties raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_properties", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_set_property(mcp_server: Client):
    """clip_set_property sets a property on a clip."""
    result = await mcp_server.call_tool("clip_set_property", {
        "clip_name": "clip01",
        "key": "Clip Name",
        "value": "renamed_clip",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_set_property_clip_not_found(mcp_server: Client):
    """clip_set_property raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_set_property", {
            "clip_name": "nonexistent",
            "key": "Clip Name",
            "value": "test",
        })


# ===================================================================
# Color — clip_get_color, clip_set_color, clip_clear_color
# ===================================================================

@pytest.mark.asyncio
async def test_clip_get_color(mcp_server: Client):
    """clip_get_color returns the label color for a clip."""
    result = await mcp_server.call_tool("clip_get_color", {"clip_name": "clip01"})
    assert extract_data(result) == "Orange"


@pytest.mark.asyncio
async def test_clip_get_color_clip_not_found(mcp_server: Client):
    """clip_get_color raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_color", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_set_color(mcp_server: Client):
    """clip_set_color applies a color label to a clip."""
    result = await mcp_server.call_tool("clip_set_color", {
        "clip_name": "clip01",
        "color": "Blue",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_set_color_clip_not_found(mcp_server: Client):
    """clip_set_color raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_set_color", {
            "clip_name": "nonexistent",
            "color": "Blue",
        })


@pytest.mark.asyncio
async def test_clip_clear_color(mcp_server: Client):
    """clip_clear_color removes the color label from a clip."""
    result = await mcp_server.call_tool("clip_clear_color", {"clip_name": "clip01"})
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_clear_color_clip_not_found(mcp_server: Client):
    """clip_clear_color raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_clear_color", {"clip_name": "nonexistent"})


# ===================================================================
# Markers — clip_add_marker, clip_get_markers, clip_delete_marker
# ===================================================================

@pytest.mark.asyncio
async def test_clip_add_marker(mcp_server: Client):
    """clip_add_marker adds a marker at a given frame."""
    result = await mcp_server.call_tool("clip_add_marker", {
        "clip_name": "clip01",
        "frame_id": 50,
        "color": "Red",
        "name": "Test Marker",
        "note": "A test note",
        "duration": 5,
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_add_marker_minimal(mcp_server: Client):
    """clip_add_marker works with only required params."""
    result = await mcp_server.call_tool("clip_add_marker", {
        "clip_name": "clip01",
        "frame_id": 0,
        "color": "Blue",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_add_marker_clip_not_found(mcp_server: Client):
    """clip_add_marker raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_add_marker", {
            "clip_name": "nonexistent",
            "frame_id": 10,
            "color": "Blue",
        })


@pytest.mark.asyncio
async def test_clip_get_markers(mcp_server: Client):
    """clip_get_markers returns the markers dict for a clip."""
    result = await mcp_server.call_tool("clip_get_markers", {"clip_name": "clip01"})
    data = extract_data(result)
    assert isinstance(data, dict)
    # MockMediaPoolItem returns marker at frame 100 with color "Blue"
    assert "100" in data or 100 in data


@pytest.mark.asyncio
async def test_clip_get_markers_clip_not_found(mcp_server: Client):
    """clip_get_markers raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_markers", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_delete_marker(mcp_server: Client):
    """clip_delete_marker removes a marker at a specific frame."""
    result = await mcp_server.call_tool("clip_delete_marker", {
        "clip_name": "clip01",
        "frame_id": 100,
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_delete_marker_clip_not_found(mcp_server: Client):
    """clip_delete_marker raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_delete_marker", {
            "clip_name": "nonexistent",
            "frame_id": 100,
        })


# ===================================================================
# Flags — clip_add_flag, clip_get_flags, clip_clear_flags
# ===================================================================

@pytest.mark.asyncio
async def test_clip_add_flag(mcp_server: Client):
    """clip_add_flag adds a flag of a given color to a clip."""
    result = await mcp_server.call_tool("clip_add_flag", {
        "clip_name": "clip01",
        "color": "Green",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_add_flag_clip_not_found(mcp_server: Client):
    """clip_add_flag raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_add_flag", {
            "clip_name": "nonexistent",
            "color": "Green",
        })


@pytest.mark.asyncio
async def test_clip_get_flags(mcp_server: Client):
    """clip_get_flags returns the list of flag colors on a clip."""
    result = await mcp_server.call_tool("clip_get_flags", {"clip_name": "clip01"})
    data = extract_data(result)
    assert isinstance(data, list)
    assert "Blue" in data


@pytest.mark.asyncio
async def test_clip_get_flags_clip_not_found(mcp_server: Client):
    """clip_get_flags raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_flags", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_clear_flags(mcp_server: Client):
    """clip_clear_flags removes a specific flag color from a clip."""
    result = await mcp_server.call_tool("clip_clear_flags", {
        "clip_name": "clip01",
        "color": "Blue",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_clear_flags_clip_not_found(mcp_server: Client):
    """clip_clear_flags raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_clear_flags", {
            "clip_name": "nonexistent",
            "color": "Blue",
        })


# ===================================================================
# Proxy — clip_link_proxy, clip_replace, clip_unlink_proxy
# ===================================================================

@pytest.mark.asyncio
async def test_clip_link_proxy(mcp_server: Client):
    """clip_link_proxy links a proxy media file to a clip."""
    result = await mcp_server.call_tool("clip_link_proxy", {
        "clip_name": "clip01",
        "proxy_path": "/media/proxy/clip01_proxy.mov",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_link_proxy_clip_not_found(mcp_server: Client):
    """clip_link_proxy raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_link_proxy", {
            "clip_name": "nonexistent",
            "proxy_path": "/media/proxy/clip_proxy.mov",
        })


@pytest.mark.asyncio
async def test_clip_replace(mcp_server: Client):
    """clip_replace replaces a clip's media file."""
    result = await mcp_server.call_tool("clip_replace", {
        "clip_name": "clip01",
        "new_file_path": "/media/replacement.mov",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_replace_clip_not_found(mcp_server: Client):
    """clip_replace raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_replace", {
            "clip_name": "nonexistent",
            "new_file_path": "/media/replacement.mov",
        })


@pytest.mark.asyncio
async def test_clip_unlink_proxy(mcp_server: Client):
    """clip_unlink_proxy removes the proxy link from a clip."""
    result = await mcp_server.call_tool("clip_unlink_proxy", {"clip_name": "clip01"})
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_unlink_proxy_clip_not_found(mcp_server: Client):
    """clip_unlink_proxy raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_unlink_proxy", {"clip_name": "nonexistent"})


# ===================================================================
# Transcription — clip_transcribe_audio, clip_get_transcript,
#                  clip_clear_transcript
# ===================================================================

@pytest.mark.asyncio
async def test_clip_transcribe_audio(mcp_server: Client):
    """clip_transcribe_audio initiates transcription on a clip."""
    result = await mcp_server.call_tool("clip_transcribe_audio", {
        "clip_name": "clip01",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_transcribe_audio_clip_not_found(mcp_server: Client):
    """clip_transcribe_audio raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_transcribe_audio", {
            "clip_name": "nonexistent",
        })


@pytest.mark.asyncio
async def test_clip_get_transcript(mcp_server: Client):
    """clip_get_transcript returns the transcript text for a clip."""
    result = await mcp_server.call_tool("clip_get_transcript", {"clip_name": "clip01"})
    text = extract_data(result)
    assert isinstance(text, str)
    assert "transcript" in text.lower()


@pytest.mark.asyncio
async def test_clip_get_transcript_clip_not_found(mcp_server: Client):
    """clip_get_transcript raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_get_transcript", {"clip_name": "nonexistent"})


@pytest.mark.asyncio
async def test_clip_clear_transcript(mcp_server: Client):
    """clip_clear_transcript clears the transcript from a clip."""
    result = await mcp_server.call_tool("clip_clear_transcript", {"clip_name": "clip01"})
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_clear_transcript_clip_not_found(mcp_server: Client):
    """clip_clear_transcript raises when clip does not exist."""
    with pytest.raises(Exception, match="not found"):
        await mcp_server.call_tool("clip_clear_transcript", {"clip_name": "nonexistent"})
