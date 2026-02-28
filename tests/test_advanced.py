"""Tests for advanced tools added in Stage 2: timeline export, compound clips,
transcription, takes, project database, unique IDs, and validation."""

from __future__ import annotations

import pytest
from fastmcp import Client

from conftest import extract_data


# ===================================================================
# Timeline Export
# ===================================================================

@pytest.mark.asyncio
async def test_timeline_export_aaf(mcp_server: Client):
    """timeline_export exports to AAF."""
    result = await mcp_server.call_tool("timeline_export", {
        "file_path": "/tmp/out.aaf",
        "export_type": "AAF",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_timeline_export_edl_with_subtype(mcp_server: Client):
    """timeline_export exports EDL with CMX 3600 subtype."""
    result = await mcp_server.call_tool("timeline_export", {
        "file_path": "/tmp/out.edl",
        "export_type": "EDL",
        "export_subtype": "CMX 3600",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_timeline_export_fcpxml(mcp_server: Client):
    """timeline_export exports to FCPXML."""
    result = await mcp_server.call_tool("timeline_export", {
        "file_path": "/tmp/out.fcpxml",
        "export_type": "FCPXML",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_timeline_export_invalid_type(mcp_server: Client):
    """timeline_export rejects invalid export_type."""
    with pytest.raises(Exception, match="Invalid export_type"):
        await mcp_server.call_tool("timeline_export", {
            "file_path": "/tmp/out.xyz",
            "export_type": "INVALID",
        })


@pytest.mark.asyncio
async def test_timeline_export_invalid_subtype(mcp_server: Client):
    """timeline_export rejects invalid export_subtype."""
    with pytest.raises(Exception, match="Invalid export_subtype"):
        await mcp_server.call_tool("timeline_export", {
            "file_path": "/tmp/out.edl",
            "export_type": "EDL",
            "export_subtype": "BOGUS",
        })


# ===================================================================
# Compound Clips and Fusion Clips
# ===================================================================

@pytest.mark.asyncio
async def test_timeline_create_compound_clip(mcp_server: Client):
    """timeline_create_compound_clip creates a compound clip from items."""
    result = await mcp_server.call_tool("timeline_create_compound_clip", {
        "item_names": ["Clip A", "Clip B"],
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_timeline_create_compound_clip_invalid_track(mcp_server: Client):
    """timeline_create_compound_clip rejects invalid track_type."""
    with pytest.raises(Exception, match="Invalid track_type"):
        await mcp_server.call_tool("timeline_create_compound_clip", {
            "item_names": ["Clip A"],
            "track_type": "bogus",
        })


@pytest.mark.asyncio
async def test_timeline_create_fusion_clip(mcp_server: Client):
    """timeline_create_fusion_clip creates a Fusion clip from items."""
    result = await mcp_server.call_tool("timeline_create_fusion_clip", {
        "item_names": ["Clip A"],
    })
    assert extract_data(result) is True


# ===================================================================
# Transcription
# ===================================================================

@pytest.mark.asyncio
async def test_clip_transcribe_audio(mcp_server: Client):
    """clip_transcribe_audio starts transcription."""
    result = await mcp_server.call_tool("clip_transcribe_audio", {
        "clip_name": "clip01",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_get_transcript(mcp_server: Client):
    """clip_get_transcript returns transcript text."""
    result = await mcp_server.call_tool("clip_get_transcript", {
        "clip_name": "clip01",
    })
    text = extract_data(result)
    assert "transcript" in text.lower()


@pytest.mark.asyncio
async def test_clip_clear_transcript(mcp_server: Client):
    """clip_clear_transcript clears transcript."""
    result = await mcp_server.call_tool("clip_clear_transcript", {
        "clip_name": "clip01",
    })
    assert extract_data(result) is True


# ===================================================================
# Timeline Item — Unique ID
# ===================================================================

@pytest.mark.asyncio
async def test_item_get_unique_id(mcp_server: Client):
    """item_get_unique_id returns a non-empty string."""
    result = await mcp_server.call_tool("item_get_unique_id", {
        "item_name": "Clip A",
    })
    uid = extract_data(result)
    assert uid == "unique-item-001"


# ===================================================================
# Timeline Item — Takes
# ===================================================================

@pytest.mark.asyncio
async def test_item_get_takes_count(mcp_server: Client):
    """item_get_takes_count returns the number of takes."""
    result = await mcp_server.call_tool("item_get_takes_count", {
        "item_name": "Clip A",
    })
    assert extract_data(result) == 2


@pytest.mark.asyncio
async def test_item_get_take_by_index(mcp_server: Client):
    """item_get_take_by_index returns take info."""
    result = await mcp_server.call_tool("item_get_take_by_index", {
        "item_name": "Clip A",
        "take_index": 1,
    })
    data = extract_data(result)
    assert data is not None
    assert "startFrame" in data


@pytest.mark.asyncio
async def test_item_get_take_by_index_invalid(mcp_server: Client):
    """item_get_take_by_index rejects take_index < 1."""
    with pytest.raises(Exception, match="take_index must be >= 1"):
        await mcp_server.call_tool("item_get_take_by_index", {
            "item_name": "Clip A",
            "take_index": 0,
        })


@pytest.mark.asyncio
async def test_item_select_take_by_index(mcp_server: Client):
    """item_select_take_by_index selects a take."""
    result = await mcp_server.call_tool("item_select_take_by_index", {
        "item_name": "Clip A",
        "take_index": 1,
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_item_finalize_take(mcp_server: Client):
    """item_finalize_take finalizes the current take."""
    result = await mcp_server.call_tool("item_finalize_take", {
        "item_name": "Clip A",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_item_delete_take_by_index(mcp_server: Client):
    """item_delete_take_by_index deletes a take."""
    result = await mcp_server.call_tool("item_delete_take_by_index", {
        "item_name": "Clip A",
        "take_index": 1,
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_item_delete_take_invalid_index(mcp_server: Client):
    """item_delete_take_by_index rejects take_index < 1."""
    with pytest.raises(Exception, match="take_index must be >= 1"):
        await mcp_server.call_tool("item_delete_take_by_index", {
            "item_name": "Clip A",
            "take_index": 0,
        })


# ===================================================================
# Project Database and Folder Operations
# ===================================================================

@pytest.mark.asyncio
async def test_project_folder_create(mcp_server: Client):
    """project_folder_create creates a new database folder."""
    result = await mcp_server.call_tool("project_folder_create", {
        "folder_name": "New Folder",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_folder_create_empty_name(mcp_server: Client):
    """project_folder_create rejects empty name."""
    with pytest.raises(Exception, match="cannot be empty"):
        await mcp_server.call_tool("project_folder_create", {
            "folder_name": "",
        })


@pytest.mark.asyncio
async def test_project_folder_delete(mcp_server: Client):
    """project_folder_delete deletes a folder."""
    result = await mcp_server.call_tool("project_folder_delete", {
        "folder_name": "Old Folder",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_folder_goto_root(mcp_server: Client):
    """project_folder_goto_root navigates to root."""
    result = await mcp_server.call_tool("project_folder_goto_root", {})
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_folder_goto_parent(mcp_server: Client):
    """project_folder_goto_parent navigates up one level."""
    result = await mcp_server.call_tool("project_folder_goto_parent", {})
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_get_database(mcp_server: Client):
    """project_get_database returns DB info."""
    result = await mcp_server.call_tool("project_get_database", {})
    data = extract_data(result)
    assert data["DbType"] == "Disk"
    assert data["DbName"] == "Local Database"


# ===================================================================
# Stage 2 Validation Tests
# ===================================================================

@pytest.mark.asyncio
async def test_cdl_validation_rejects_invalid_slope(mcp_server: Client):
    """color_set_cdl rejects non-RGB-triple Slope values."""
    with pytest.raises(Exception, match="3 RGB values"):
        await mcp_server.call_tool("color_set_cdl", {
            "item_name": "Clip A",
            "cdl": {
                "Slope": [1.0, 1.0],  # Only 2 values, need 3
                "Offset": [0.0, 0.0, 0.0],
                "Power": [1.0, 1.0, 1.0],
                "Saturation": 1.0,
            },
        })


@pytest.mark.asyncio
async def test_cdl_validation_accepts_valid_values(mcp_server: Client):
    """color_set_cdl accepts valid CDL values."""
    result = await mcp_server.call_tool("color_set_cdl", {
        "item_name": "Clip A",
        "cdl": {
            "Slope": [1.1, 1.0, 0.9],
            "Offset": [0.01, -0.01, 0.0],
            "Power": [1.0, 1.0, 1.0],
            "Saturation": 1.2,
        },
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_timeline_empty_name_rejected(mcp_server: Client):
    """timeline_set_name rejects empty name."""
    with pytest.raises(Exception, match="empty"):
        await mcp_server.call_tool("timeline_set_name", {"name": ""})


@pytest.mark.asyncio
async def test_timeline_whitespace_name_rejected(mcp_server: Client):
    """timeline_set_name rejects whitespace-only name."""
    with pytest.raises(Exception, match="empty"):
        await mcp_server.call_tool("timeline_set_name", {"name": "   "})


@pytest.mark.asyncio
async def test_track_type_validation(mcp_server: Client):
    """timeline_get_track_count rejects invalid track_type."""
    with pytest.raises(Exception, match="Invalid track_type"):
        await mcp_server.call_tool("timeline_get_track_count", {
            "track_type": "bogus",
        })


@pytest.mark.asyncio
async def test_track_index_validation(mcp_server: Client):
    """timeline_delete_clips rejects track_index < 1."""
    with pytest.raises(Exception, match="track_index must be >= 1"):
        await mcp_server.call_tool("timeline_delete_clips", {
            "item_names": ["Clip A"],
            "track_index": 0,
        })


# ===================================================================
# Scene Detection & Auto-Subtitles (timeline.py)
# ===================================================================

@pytest.mark.asyncio
async def test_timeline_detect_scene_cuts(mcp_server: Client):
    """timeline_detect_scene_cuts returns frame numbers of scene transitions."""
    result = await mcp_server.call_tool("timeline_detect_scene_cuts", {})
    cuts = extract_data(result)
    assert isinstance(cuts, list)
    assert cuts == [100, 250, 500]


@pytest.mark.asyncio
async def test_timeline_create_subtitles_from_audio(mcp_server: Client):
    """timeline_create_subtitles_from_audio generates subtitles."""
    result = await mcp_server.call_tool("timeline_create_subtitles_from_audio", {})
    assert extract_data(result) is True


# ===================================================================
# Timeline Settings (timeline.py)
# ===================================================================

@pytest.mark.asyncio
async def test_timeline_get_setting(mcp_server: Client):
    """timeline_get_setting reads a timeline setting by key."""
    result = await mcp_server.call_tool("timeline_get_setting", {
        "key": "timelineFrameRate",
    })
    value = extract_data(result)
    # MockTimeline.GetSetting returns "24" if "Rate" is in the key
    assert value == "24"


@pytest.mark.asyncio
async def test_timeline_set_setting(mcp_server: Client):
    """timeline_set_setting writes a timeline setting."""
    result = await mcp_server.call_tool("timeline_set_setting", {
        "key": "timelineFrameRate",
        "value": "30",
    })
    assert extract_data(result) is True


# ===================================================================
# Stabilize & Smart Reframe (timeline_item.py)
# ===================================================================

@pytest.mark.asyncio
async def test_item_stabilize(mcp_server: Client):
    """item_stabilize runs stabilization analysis on a clip."""
    result = await mcp_server.call_tool("item_stabilize", {
        "item_name": "Clip A",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_item_smart_reframe(mcp_server: Client):
    """item_smart_reframe applies smart reframe with valid settings."""
    result = await mcp_server.call_tool("item_smart_reframe", {
        "item_name": "Clip A",
        "target_ratio": "9:16",
        "motion_estimation": "better",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_item_smart_reframe_invalid_motion(mcp_server: Client):
    """item_smart_reframe rejects invalid motion_estimation."""
    with pytest.raises(Exception, match="Invalid motion_estimation"):
        await mcp_server.call_tool("item_smart_reframe", {
            "item_name": "Clip A",
            "motion_estimation": "ultra",
        })


@pytest.mark.asyncio
async def test_item_add_node(mcp_server: Client):
    """item_add_node adds a color correction node."""
    result = await mcp_server.call_tool("item_add_node", {
        "item_name": "Clip A",
    })
    assert extract_data(result) is True


# ===================================================================
# Node Labels (color.py)
# ===================================================================

@pytest.mark.asyncio
async def test_color_get_node_label(mcp_server: Client):
    """color_get_node_label returns the label for a node."""
    result = await mcp_server.call_tool("color_get_node_label", {
        "item_name": "Clip A",
        "node_index": 1,
    })
    label = extract_data(result)
    assert label == "Node 1"


@pytest.mark.asyncio
async def test_color_set_node_label(mcp_server: Client):
    """color_set_node_label sets a label on a node."""
    result = await mcp_server.call_tool("color_set_node_label", {
        "item_name": "Clip A",
        "node_index": 1,
        "label": "Primary Grade",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_color_node_label_index_validation(mcp_server: Client):
    """color_get_node_label rejects node_index < 1."""
    with pytest.raises(Exception, match="node_index must be >= 1"):
        await mcp_server.call_tool("color_get_node_label", {
            "item_name": "Clip A",
            "node_index": 0,
        })


# ===================================================================
# Replace Clip & Unlink Proxy (media_pool_item.py)
# ===================================================================

@pytest.mark.asyncio
async def test_clip_replace(mcp_server: Client):
    """clip_replace replaces a clip's media file."""
    result = await mcp_server.call_tool("clip_replace", {
        "clip_name": "clip01",
        "new_file_path": "/media/replacement.mov",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_clip_unlink_proxy(mcp_server: Client):
    """clip_unlink_proxy removes proxy link from a clip."""
    result = await mcp_server.call_tool("clip_unlink_proxy", {
        "clip_name": "clip01",
    })
    assert extract_data(result) is True


# ===================================================================
# Project Archive & Database List (project.py)
# ===================================================================

@pytest.mark.asyncio
async def test_project_archive(mcp_server: Client):
    """project_archive archives a project to .dra file."""
    result = await mcp_server.call_tool("project_archive", {
        "name": "Test Project",
        "file_path": "/tmp/backup.dra",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_archive_without_stills(mcp_server: Client):
    """project_archive works without stills and LUTs."""
    result = await mcp_server.call_tool("project_archive", {
        "name": "Test Project",
        "file_path": "/tmp/backup.dra",
        "with_stills_and_luts": False,
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_restore_archive(mcp_server: Client):
    """project_restore_archive restores from .dra archive."""
    result = await mcp_server.call_tool("project_restore_archive", {
        "file_path": "/tmp/backup.dra",
    })
    assert extract_data(result) is True


@pytest.mark.asyncio
async def test_project_get_database_list(mcp_server: Client):
    """project_get_database_list returns available databases."""
    result = await mcp_server.call_tool("project_get_database_list", {})
    db_list = extract_data(result)
    assert isinstance(db_list, list)
    assert len(db_list) == 2
    assert db_list[0]["DbType"] == "Disk"
    assert db_list[1]["DbType"] == "PostgreSQL"
