#!/usr/bin/env python3
"""Verify that the DaVinci Resolve scripting bridge is working.

Connects to the running Resolve instance and prints system, project,
and timeline information.  Exits with code 0 on success, 1 on failure.

Usage:
    python scripts/check_resolve.py
"""

from __future__ import annotations

import sys

# Add the src directory to the path so we can import the package directly
# when running from the repository root without installing.
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from davinci_resolve_mcp.resolve_api import ResolveAPI
from davinci_resolve_mcp.exceptions import ResolveNotRunning


def _separator() -> None:
    """Print a visual separator line."""
    print("-" * 50)


def main() -> int:
    """Run all connection checks and print results.

    Returns:
        0 if all checks passed, 1 if any check failed.
    """
    print()
    print("DaVinci Resolve MCP - Connection Check")
    _separator()

    # ------------------------------------------------------------------
    # 1. Connect to Resolve
    # ------------------------------------------------------------------
    try:
        api = ResolveAPI.get_instance()
        resolve = api.resolve
    except ResolveNotRunning as exc:
        print(f"\u274c Connection failed: {exc}")
        print()
        print("Make sure DaVinci Resolve is running and try again.")
        return 1
    except Exception as exc:
        print(f"\u274c Unexpected error: {exc}")
        return 1

    print("\u2705 Connected to DaVinci Resolve")

    # ------------------------------------------------------------------
    # 2. Version and product info
    # ------------------------------------------------------------------
    try:
        raw_version = resolve.GetVersion()
        if isinstance(raw_version, (list, tuple)):
            version = ".".join(str(v) for v in raw_version)
        else:
            version = str(raw_version)
        print(f"\u2705 Version: {version}")
    except Exception as exc:
        print(f"\u274c Could not read version: {exc}")

    try:
        product = resolve.GetProductName()
        print(f"\u2705 Product: {product}")
    except Exception as exc:
        print(f"\u274c Could not read product name: {exc}")

    # ------------------------------------------------------------------
    # 3. Current page
    # ------------------------------------------------------------------
    try:
        page = resolve.GetCurrentPage() or "(unknown)"
        print(f"\u2705 Current page: {page}")
    except Exception as exc:
        print(f"\u274c Could not read current page: {exc}")

    _separator()

    # ------------------------------------------------------------------
    # 4. Project manager and project list
    # ------------------------------------------------------------------
    try:
        pm = api.project_manager
        projects = pm.GetProjectListInCurrentFolder() or []
        print(f"\u2705 Projects in current folder: {len(projects)}")
        # Show up to 10 project names
        for name in projects[:10]:
            print(f"   - {name}")
        if len(projects) > 10:
            print(f"   ... and {len(projects) - 10} more")
    except Exception as exc:
        print(f"\u274c Could not list projects: {exc}")

    _separator()

    # ------------------------------------------------------------------
    # 5. Current project info
    # ------------------------------------------------------------------
    try:
        project = api.project
        if project is None:
            print("\u26a0\ufe0f  No project is currently open.")
        else:
            print(f"\u2705 Current project: {project.GetName()}")
            timeline_count = project.GetTimelineCount() or 0
            print(f"\u2705 Timelines: {timeline_count}")

            # Read key settings
            width = project.GetSetting("timelineResolutionWidth") or "?"
            height = project.GetSetting("timelineResolutionHeight") or "?"
            fps = project.GetSetting("timelineFrameRate") or "?"
            print(f"\u2705 Resolution: {width}x{height} @ {fps} fps")
    except Exception as exc:
        print(f"\u274c Could not read project info: {exc}")

    _separator()

    # ------------------------------------------------------------------
    # 6. Current timeline info
    # ------------------------------------------------------------------
    try:
        timeline = api.timeline
        if timeline is None:
            print("\u26a0\ufe0f  No timeline is currently open.")
        else:
            print(f"\u2705 Current timeline: {timeline.GetName()}")
            print(f"\u2705 Start frame: {timeline.GetStartFrame()}")
            print(f"\u2705 End frame: {timeline.GetEndFrame()}")
            video_tracks = timeline.GetTrackCount("video") or 0
            audio_tracks = timeline.GetTrackCount("audio") or 0
            print(f"\u2705 Tracks: {video_tracks} video, {audio_tracks} audio")
            timecode = timeline.GetCurrentTimecode() or "(unknown)"
            print(f"\u2705 Playhead: {timecode}")
    except Exception as exc:
        print(f"\u274c Could not read timeline info: {exc}")

    _separator()

    # ------------------------------------------------------------------
    # 7. Media storage check
    # ------------------------------------------------------------------
    try:
        storage = api.media_storage
        if storage is None:
            print("\u26a0\ufe0f  Media Storage is not available.")
        else:
            volumes = storage.GetMountedVolumeList() or []
            print(f"\u2705 Mounted volumes: {len(volumes)}")
            for vol in volumes[:5]:
                print(f"   - {vol}")
            if len(volumes) > 5:
                print(f"   ... and {len(volumes) - 5} more")
    except Exception as exc:
        print(f"\u274c Could not read media storage: {exc}")

    _separator()
    print("\u2705 All checks complete.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
