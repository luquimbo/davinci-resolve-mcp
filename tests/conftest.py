"""Shared test fixtures: mock DaVinci Resolve hierarchy and FastMCP server.

The mock classes mirror the real Resolve scripting bridge so that tool modules
can call GetVersion(), GetProjectManager(), etc. without a running instance.
Two key fixtures are exported:

* ``mock_resolve``  — patches ResolveAPI singleton to use the mock hierarchy.
* ``mcp_server``    — a ready-to-use FastMCP Client with all tools registered.

A helper function ``extract_data`` is also provided to work around a FastMCP
quirk where ``list[dict]`` return types are not properly deserialized via
``.data``.  Use ``extract_data(result)`` in all tests for consistency.
"""

from __future__ import annotations

import importlib
import json
import sys
from typing import Any
from unittest.mock import patch

import pytest
import pytest_asyncio
from fastmcp import Client, FastMCP

from davinci_resolve_mcp.resolve_api import ResolveAPI


# ---------------------------------------------------------------------------
# Mock DaVinci Resolve scripting bridge
# ---------------------------------------------------------------------------

class MockFusionTool:
    """Simulates a single Fusion node/tool with basic attributes."""

    def GetAttrs(self, key: str | None = None) -> str | dict:
        # When called with a specific key, return that attribute value;
        # when called with no args, return the full attribute dict.
        attrs = {"TOOLS_Name": "Background1"}
        if key is not None:
            return attrs.get(key, "")
        return attrs


class MockFusionComp:
    """Simulates a Fusion composition containing tools."""

    def GetToolList(self) -> dict:
        return {"tool1": MockFusionTool()}


class MockStill:
    """Simulates a gallery still image reference."""

    def GetLabel(self) -> str:
        return "Still 1"


class MockAlbum:
    """Simulates a gallery still album with a label and stills list."""

    def __init__(self, label: str = "Stills 1") -> None:
        self._label = label

    def GetLabel(self) -> str:
        return self._label

    def GetStills(self) -> list:
        return [MockStill()]

    def ImportStills(self, paths: list[str]) -> bool:
        return True

    def ExportStills(self, stills: list, path: str, *args: Any) -> bool:
        return True

    def DeleteStills(self, stills: list) -> bool:
        return True

    def GrabStill(self) -> bool:
        return True


class MockGallery:
    """Simulates the Gallery object returned by Project.GetGallery()."""

    def __init__(self) -> None:
        self._album = MockAlbum("Stills 1")

    def GetGalleryStillAlbums(self) -> list:
        return [self._album]

    def GetCurrentStillAlbum(self) -> MockAlbum:
        return self._album

    def SetCurrentStillAlbum(self, album: Any) -> bool:
        return True

    def CreateGalleryStillAlbum(self, name: str) -> MockAlbum:
        return MockAlbum(name)

    def DeleteGalleryStillAlbum(self, album: Any) -> bool:
        return True

    def GetGalleryPowerGradeAlbums(self) -> list:
        return [MockAlbum("PowerGrade 1")]

    def SetCurrentPowerGradeAlbum(self, album: Any) -> bool:
        return True


class MockMediaPoolItem:
    """Simulates a single clip in the Media Pool with properties and markers."""

    def __init__(self, name: str = "clip01") -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name

    def SetClipProperty(self, key: str, value: str) -> bool:
        return True

    def GetClipProperty(self, key: str | None = None) -> dict | str:
        # When called with a specific key, return a simple string
        if key is not None:
            prop_map = {
                "Clip Name": self._name,
                "Duration": "00:01:00:00",
                "FPS": "24",
                "Resolution": "1920x1080",
                "File Path": f"/media/{self._name}.mov",
            }
            return prop_map.get(key, "")

        # When called with no args, return the full property dict
        return {
            "Clip Name": self._name,
            "Duration": "00:01:00:00",
            "FPS": "24",
            "Resolution": "1920x1080",
            "Clip Color": "Orange",
        }

    def GetMetadata(self, key: str | None = None) -> dict:
        return {"Reel": "A001"}

    def SetMetadata(self, key: str, value: str) -> bool:
        return True

    def GetClipColor(self) -> str:
        return "Orange"

    def SetClipColor(self, color: str) -> bool:
        return True

    def ClearClipColor(self) -> bool:
        return True

    def AddMarker(
        self,
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        return True

    def GetMarkers(self) -> dict:
        return {
            100: {
                "color": "Blue",
                "name": "M1",
                "note": "",
                "duration": 1,
                "customData": "",
            }
        }

    def DeleteMarkerAtFrame(self, frame_id: int) -> bool:
        return True

    def AddFlag(self, color: str) -> bool:
        return True

    def GetFlagList(self) -> list[str]:
        return ["Blue"]

    def ClearFlags(self, color: str) -> bool:
        return True

    def LinkProxyMedia(self, path: str) -> bool:
        return True

    def ReplaceClip(self, path: str) -> bool:
        return True

    def UnlinkProxyMedia(self) -> bool:
        return True

    def TranscribeAudio(self) -> bool:
        return True

    def GetTranscriptText(self) -> str:
        return "Hello world, this is a test transcript."

    def ClearTranscriptText(self) -> bool:
        return True


class MockFolder:
    """Simulates a Media Pool folder with clips and subfolders."""

    def __init__(self, name: str = "Master") -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name

    def GetClipList(self) -> list[MockMediaPoolItem]:
        return [
            MockMediaPoolItem("clip01"),
            MockMediaPoolItem("clip02"),
        ]

    def GetSubFolderList(self) -> list["MockFolder"]:
        return [MockFolder("Sub")]


class MockTimelineItem:
    """Simulates a clip placed on a timeline track."""

    def __init__(self, name: str = "Clip A") -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name

    def GetDuration(self) -> int:
        return 100

    def GetStart(self) -> int:
        return 0

    def GetEnd(self) -> int:
        return 100

    def GetProperty(self, key: str | None = None) -> dict | Any:
        props = {
            "ZoomX": 1.0,
            "ZoomY": 1.0,
            "Pan": 0.0,
            "Tilt": 0.0,
            "RotationAngle": 0.0,
            "AnchorPointX": 0.0,
            "AnchorPointY": 0.0,
            "CropLeft": 0.0,
            "CropRight": 0.0,
            "CropTop": 0.0,
            "CropBottom": 0.0,
            "CompositeMode": "Normal",
            "Opacity": 100.0,
        }
        if key is not None:
            return props.get(key)
        return props

    def SetProperty(self, key: str, value: Any) -> bool:
        return True

    def GetClipColor(self) -> str:
        return ""

    def SetClipColor(self, color: str) -> bool:
        return True

    def SetClipEnabled(self, enabled: bool) -> bool:
        return True

    def AddMarker(
        self,
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        return True

    def GetMarkers(self) -> dict:
        return {}

    def DeleteMarkerAtFrame(self, frame_id: int) -> bool:
        return True

    def AddFlag(self, color: str) -> bool:
        return True

    def GetFlagList(self) -> list:
        return []

    def GetMediaPoolItem(self) -> MockMediaPoolItem:
        return MockMediaPoolItem(self._name)

    def GetLinkedItems(self) -> list:
        return []

    def GetNumNodes(self) -> int:
        return 3

    def SetLUT(self, node_index: int, path: str) -> bool:
        return True

    def GetLUT(self, node_index: int) -> str:
        return "/path/to/lut.cube"

    def SetCDL(self, cdl: dict) -> bool:
        return True

    def GetCDL(self) -> dict:
        return {
            "Slope": [1, 1, 1],
            "Offset": [0, 0, 0],
            "Power": [1, 1, 1],
            "Saturation": 1.0,
        }

    def ExportLUT(self, lut_type: int, path: str) -> bool:
        return True

    def GetVersionNameList(self, version_type: int) -> list[str]:
        return ["Version 1", "Default"]

    def AddVersion(self, name: str, version_type: int) -> bool:
        return True

    def SetCurrentVersion(self, name: str, version_type: int) -> bool:
        return True

    def GetCurrentVersion(self, version_type: int) -> dict:
        return {"versionName": "Default"}

    def DeleteVersion(self, name: str, version_type: int) -> bool:
        return True

    def RenameVersion(self, old: str, new: str, version_type: int) -> bool:
        return True

    def LoadVersion(self, name: str, version_type: int) -> bool:
        return True

    def GetFusionCompCount(self) -> int:
        return 1

    def GetFusionCompNameList(self) -> list[str]:
        return ["Comp 1"]

    def GetFusionCompByName(self, name: str) -> MockFusionComp:
        return MockFusionComp()

    def AddFusionComp(self) -> bool:
        return True

    def ImportFusionComp(self, path: str) -> bool:
        return True

    def ExportFusionComp(self, name: str, path: str) -> bool:
        return True

    def DeleteFusionCompByName(self, name: str) -> bool:
        return True

    def RenameFusionCompByName(self, old_name: str, new_name: str) -> bool:
        return True

    def SetNodeEnabled(self, node_index: int, enabled: bool) -> bool:
        return True

    def SetGroupMembership(self, group_id: str, member: bool) -> bool:
        return True

    def ApplyGradeFromGalleryStill(self, still: Any) -> bool:
        return True

    def GetUniqueId(self) -> str:
        return "unique-item-001"

    def GetTakesCount(self) -> int:
        return 2

    def GetTakeByIndex(self, idx: int) -> dict | None:
        if idx <= 2:
            return {"startFrame": 0, "endFrame": 100, "mediaPoolItem": None}
        return None

    def SelectTakeByIndex(self, idx: int) -> bool:
        return idx <= 2

    def FinalizeTake(self) -> bool:
        return True

    def DeleteTakeByIndex(self, idx: int) -> bool:
        return idx <= 2

    def Stabilize(self) -> bool:
        return True

    def SmartReframe(self, settings: dict) -> bool:
        return True

    def AddNode(self) -> bool:
        return True

    def GetNodeLabel(self, index: int) -> str:
        return f"Node {index}"

    def SetNodeLabel(self, index: int, label: str) -> bool:
        return True


class MockTimeline:
    """Simulates a DaVinci Resolve timeline object."""

    def __init__(self, name: str = "Timeline 1") -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name

    def SetName(self, name: str) -> bool:
        self._name = name
        return True

    def GetStartFrame(self) -> int:
        return 0

    def GetEndFrame(self) -> int:
        return 1000

    def GetTrackCount(self, track_type: str) -> int:
        return 3

    def AddTrack(self, track_type: str) -> bool:
        return True

    def DeleteTrack(self, track_type: str, index: int) -> bool:
        return True

    def GetTrackName(self, track_type: str, index: int) -> str:
        return f"Video {index}" if track_type == "video" else f"Audio {index}"

    def SetTrackName(self, track_type: str, index: int, name: str) -> bool:
        return True

    def SetTrackEnable(self, track_type: str, index: int, enabled: bool) -> bool:
        return True

    def SetTrackLock(self, track_type: str, index: int, locked: bool) -> bool:
        return True

    def GetItemListInTrack(self, track_type: str, index: int) -> list[MockTimelineItem]:
        return [MockTimelineItem("Clip A"), MockTimelineItem("Clip B")]

    def GetCurrentTimecode(self) -> str:
        return "01:00:00:00"

    def SetCurrentTimecode(self, timecode: str) -> bool:
        return True

    def GetCurrentVideoItem(self) -> MockTimelineItem:
        return MockTimelineItem("Clip A")

    def GetStartTimecode(self) -> str:
        return "01:00:00:00"

    def DuplicateTimeline(self) -> "MockTimeline":
        return MockTimeline(f"{self._name} copy")

    def AddMarker(
        self,
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        return True

    def GetMarkers(self) -> dict:
        return {}

    def DeleteMarkerAtFrame(self, frame_id: int) -> bool:
        return True

    def DeleteClips(self, items: list) -> bool:
        return True

    def ApplyGradeFromDRX(self, path: str, mode: int, *items: Any) -> bool:
        return True

    def GrabStill(self) -> bool:
        return True

    def ExportAsFile(self, path: str, export_type: str, export_subtype: str = "") -> bool:
        return True

    def CreateCompoundClip(self, items: list, clip_info: dict) -> Any:
        return MockTimelineItem("Compound Clip")

    def CreateFusionClip(self, items: list) -> Any:
        return MockTimelineItem("Fusion Clip")

    def DetectSceneCuts(self) -> list[int]:
        return [100, 250, 500]

    def CreateSubtitlesFromAudio(self) -> bool:
        return True

    def GetSetting(self, key: str) -> str:
        return "24" if "Rate" in key else "1920"

    def SetSetting(self, key: str, value: str) -> bool:
        return True


class MockMediaPool:
    """Simulates the project's Media Pool with folders, clips, and timelines."""

    def GetRootFolder(self) -> MockFolder:
        return MockFolder("Master")

    def GetCurrentFolder(self) -> MockFolder:
        return MockFolder("Rushes")

    def SetCurrentFolder(self, folder: Any) -> bool:
        return True

    def AddSubFolder(self, parent: Any, name: str) -> MockFolder:
        return MockFolder(name)

    def DeleteFolders(self, folders: list) -> bool:
        return True

    def ImportMedia(self, paths: list[str]) -> list[MockMediaPoolItem]:
        return [MockMediaPoolItem("imported_clip")]

    def CreateEmptyTimeline(self, name: str) -> MockTimeline:
        return MockTimeline(name)

    def CreateTimelineFromClips(self, name: str, clips: list) -> MockTimeline:
        return MockTimeline(name)

    def DeleteClips(self, clips: list) -> bool:
        return True

    def MoveClips(self, clips: list, folder: Any) -> bool:
        return True

    def RelinkClips(self, clips: list, path: str) -> bool:
        return True

    def ExportMetadata(self, path: str, clips: list) -> bool:
        return True

    def AppendToTimeline(self, clips_or_dicts: list) -> list[MockTimelineItem]:
        return [MockTimelineItem()]


class MockMediaStorage:
    """Simulates Resolve's storage browser for mounted volumes."""

    def GetMountedVolumeList(self) -> list[str]:
        return ["/Volumes/Media"]

    def GetSubFolderList(self, path: str) -> list[str]:
        return ["Footage", "Audio"]

    def GetFileList(self, path: str) -> list[str]:
        return ["clip01.mov", "clip02.mp4"]

    def AddItemListToMediaPool(self, paths: list[str]) -> list[MockMediaPoolItem]:
        return [MockMediaPoolItem("clip01")]


class MockProject:
    """Simulates a DaVinci Resolve project with timelines, media pool, and render queue."""

    def GetName(self) -> str:
        return "Test Project"

    def SaveProject(self) -> bool:
        return True

    def ExportProject(self, path: str, with_stills: bool = True) -> bool:
        return True

    def GetSetting(self, key: str) -> str:
        # Return realistic values for common settings
        if "Width" in key:
            return "1920"
        return "24"

    def SetSetting(self, key: str, value: str) -> bool:
        return True

    def GetTimelineCount(self) -> int:
        return 2

    def GetTimelineByIndex(self, index: int) -> MockTimeline | None:
        if index <= 2:
            return MockTimeline(f"Timeline {index}")
        return None

    def SetCurrentTimeline(self, timeline: Any) -> bool:
        return True

    def GetCurrentTimeline(self) -> MockTimeline:
        return MockTimeline()

    def GetMediaPool(self) -> MockMediaPool:
        return MockMediaPool()

    def GetGallery(self) -> MockGallery:
        return MockGallery()

    # -- Render queue --

    def GetRenderFormats(self) -> dict:
        return {"mp4": "MP4", "mov": "QuickTime"}

    def GetRenderCodecs(self, format_name: str) -> dict:
        return {"H.264": "H.264", "H.265": "H.265"}

    def GetRenderPresetList(self) -> list[str]:
        return ["YouTube 1080p", "ProRes Master"]

    def LoadRenderPreset(self, name: str) -> bool:
        return True

    def SetRenderSettings(self, settings: dict) -> bool:
        return True

    def GetCurrentRenderFormatAndCodec(self) -> dict:
        return {"format": "mp4", "codec": "H.264"}

    def SetCurrentRenderFormatAndCodec(self, fmt: str, codec: str) -> bool:
        return True

    def AddRenderJob(self) -> str:
        return "job-001"

    def DeleteRenderJob(self, job_id: str) -> bool:
        return True

    def DeleteAllRenderJobs(self) -> bool:
        return True

    def GetRenderJobList(self) -> list[dict]:
        return [
            {
                "JobId": "job-001",
                "RenderStatus": "Ready",
                "TimelineName": "Timeline 1",
                "TargetDir": "/tmp",
                "OutputFilename": "out.mp4",
            }
        ]

    def StartRendering(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def StopRendering(self) -> None:
        return None

    def GetRenderJobStatus(self, job_id: str) -> dict:
        return {"JobStatus": "Complete", "CompletionPercentage": 100}

    def GetColorGroupsList(self) -> list[dict]:
        return [{"name": "Group 1", "id": "group-001"}]

    def AddColorGroup(self, name: str) -> bool:
        return True

    def DeleteColorGroup(self, group_id: str) -> bool:
        return True

    def GetFairlightPresetList(self) -> list[str]:
        return ["Dialogue", "Music", "SFX"]

    def ApplyFairlightPreset(self, name: str, *args: Any) -> bool:
        return True


class MockProjectManager:
    """Simulates the project manager that lists, creates, and switches projects."""

    def GetProjectListInCurrentFolder(self) -> list[str]:
        return ["Project A", "Project B"]

    def GetCurrentProject(self) -> MockProject:
        return MockProject()

    def CreateProject(self, name: str) -> MockProject | None:
        # Simulate failure when name is "Existing" (duplicate)
        if name == "Existing":
            return None
        return MockProject()

    def LoadProject(self, name: str) -> bool:
        return True

    def CloseProject(self, project: Any) -> bool:
        return True

    def DeleteProject(self, name: str) -> bool:
        return True

    def ImportProject(self, path: str) -> bool:
        return True

    def GetFolderListInCurrentFolder(self) -> list[str]:
        return ["Folder1"]

    def OpenFolder(self, name: str) -> bool:
        return True

    def CreateFolder(self, name: str) -> bool:
        return True

    def DeleteFolder(self, name: str) -> bool:
        return True

    def GotoRootFolder(self) -> bool:
        return True

    def GotoParentFolder(self) -> bool:
        return True

    def GetCurrentDatabase(self) -> dict:
        return {"DbType": "Disk", "DbName": "Local Database"}

    def ArchiveProject(self, name: str, path: str, with_stills: bool = True) -> bool:
        return True

    def RestoreProject(self, path: str) -> bool:
        return True

    def GetDatabaseList(self) -> list[dict]:
        return [
            {"DbType": "Disk", "DbName": "Local Database"},
            {"DbType": "PostgreSQL", "DbName": "Remote DB", "IpAddress": "192.168.1.100"},
        ]


class MockResolve:
    """Top-level mock of the DaVinci Resolve scripting bridge.

    Mimics the object returned by ``scriptapp("Resolve")``.
    """

    def GetVersion(self) -> list[int]:
        return [19, 1, 2]

    def GetProductName(self) -> str:
        return "DaVinci Resolve Studio"

    def GetCurrentPage(self) -> str:
        return "edit"

    def OpenPage(self, page: str) -> bool:
        return True

    def GetMediaStorage(self) -> MockMediaStorage:
        return MockMediaStorage()

    def GetProjectManager(self) -> MockProjectManager:
        return MockProjectManager()


# ---------------------------------------------------------------------------
# Test helper — reliable data extraction from call_tool results
# ---------------------------------------------------------------------------

def extract_data(result: Any) -> Any:
    """Extract the tool's return value from a ``CallToolResult``.

    FastMCP's ``result.data`` works perfectly for primitives (str, int, bool),
    flat dicts, and lists of primitives.  However, for ``list[dict]`` return
    types, ``.data`` may wrap inner dicts into opaque dataclass objects.

    This helper falls back to JSON-parsing the text content when ``.data``
    contains those opaque wrappers, giving tests a reliable plain-Python
    value in all cases.
    """
    data = result.data

    # Fast path: .data is usable for most types
    if data is None or isinstance(data, (str, int, float, bool)):
        return data

    # For dicts, .data is fine — FastMCP deserializes them correctly
    if isinstance(data, dict):
        return data

    # For lists, check if elements are plain Python types
    if isinstance(data, list):
        if not data:
            return data
        # If the first element is a basic type, .data is fine
        if isinstance(data[0], (str, int, float, bool, dict, list)):
            return data
        # Otherwise the elements are opaque wrappers — fall back to JSON
        text = result.content[0].text if result.content else "null"
        return json.loads(text)

    # Fallback for any other type: parse from JSON text content
    text = result.content[0].text if result.content else "null"
    return json.loads(text)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_resolve(monkeypatch: pytest.MonkeyPatch) -> MockResolve:
    """Patch ``ResolveAPI`` singleton to use the mock Resolve hierarchy.

    Sets ``ResolveAPI._instance`` to a pre-configured instance where
    ``_resolve`` points to a ``MockResolve``, and ``_load_resolve_script``
    is neutralised so no real DaVinci Resolve import is attempted.

    Returns the ``MockResolve`` instance for direct assertions in tests.
    """
    # Reset any previous singleton state
    ResolveAPI.reset()

    # Build a pre-configured ResolveAPI instance with mock references
    mock = MockResolve()
    api = ResolveAPI()
    api._resolve = mock
    # Prevent _load_resolve_script from importing the real Resolve module
    api._script_module = type("FakeModule", (), {"scriptapp": staticmethod(lambda _: mock)})()

    # Install our instance as the singleton
    monkeypatch.setattr(ResolveAPI, "_instance", api)

    yield mock

    # Cleanup: ensure the singleton is cleared after the test
    ResolveAPI.reset()


@pytest_asyncio.fixture()
async def mcp_server(mock_resolve: MockResolve) -> Client:
    """Create a FastMCP server with all tool modules registered and return a Client.

    The ``mock_resolve`` fixture is a dependency, so the ResolveAPI singleton
    is pre-configured before any tool code runs.

    Returns a connected ``Client`` instance you can use with ``call_tool()``.
    """
    from davinci_resolve_mcp.tools import (
        playback,
        project,
        media_storage,
        media_pool,
        media_pool_item,
        timeline,
        timeline_item,
        render,
        color,
        fusion,
        gallery,
        fairlight,
    )
    from davinci_resolve_mcp.resources import system_info, project_info, timeline_info

    # Create a fresh MCP server for this test session
    mcp = FastMCP("DaVinci Resolve Test")

    # Register all tool modules
    tool_modules = [
        playback,
        project,
        media_storage,
        media_pool,
        media_pool_item,
        timeline,
        timeline_item,
        render,
        color,
        fusion,
        gallery,
        fairlight,
    ]

    for mod in tool_modules:
        mod.register(mcp)

    # Register resource modules
    for res_mod in [system_info, project_info, timeline_info]:
        res_mod.register(mcp)

    # Create and yield a connected in-memory client
    async with Client(mcp) as client:
        yield client
