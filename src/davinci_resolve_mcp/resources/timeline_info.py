"""MCP Resource: resolve://timeline — current timeline tracks, duration, timecode."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from ..resolve_api import ResolveAPI
from ..exceptions import ResolveNotRunning


def register(mcp: FastMCP) -> None:
    """Register the resolve://timeline resource."""

    @mcp.resource("resolve://timeline")
    def timeline_info() -> str:
        """Current DaVinci Resolve timeline information.

        Returns JSON with:
        - name: Timeline name
        - start_frame / end_frame: Frame range
        - video_tracks / audio_tracks: Track counts
        - start_timecode: Start timecode string
        - current_timecode: Playhead timecode
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline

            if tl is None:
                return json.dumps({
                    "error": "No timeline is currently open.",
                    "name": None,
                })

            return json.dumps({
                "name": tl.GetName(),
                "start_frame": tl.GetStartFrame(),
                "end_frame": tl.GetEndFrame(),
                "video_tracks": tl.GetTrackCount("video") or 0,
                "audio_tracks": tl.GetTrackCount("audio") or 0,
                "start_timecode": tl.GetStartTimecode() or "",
                "current_timecode": tl.GetCurrentTimecode() or "",
            })
        except ResolveNotRunning:
            return json.dumps({
                "error": "DaVinci Resolve is not running.",
                "name": None,
            })
        except Exception as exc:
            return json.dumps({"error": str(exc)})
