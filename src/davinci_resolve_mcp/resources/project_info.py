"""MCP Resource: resolve://project — current project name, settings, timeline count."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from ..resolve_api import ResolveAPI
from ..exceptions import ResolveNotRunning


def register(mcp: FastMCP) -> None:
    """Register the resolve://project resource."""

    @mcp.resource("resolve://project")
    def project_info() -> str:
        """Current DaVinci Resolve project information.

        Returns JSON with:
        - name: Project name
        - timeline_count: Number of timelines
        - resolution: Project resolution (width x height)
        - frame_rate: Timeline frame rate
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project

            if project is None:
                return json.dumps({
                    "error": "No project is currently open.",
                    "name": None,
                })

            # Read a few key settings for context
            width = project.GetSetting("timelineResolutionWidth") or "unknown"
            height = project.GetSetting("timelineResolutionHeight") or "unknown"
            fps = project.GetSetting("timelineFrameRate") or "unknown"

            return json.dumps({
                "name": project.GetName(),
                "timeline_count": project.GetTimelineCount() or 0,
                "resolution": f"{width}x{height}",
                "frame_rate": fps,
            })
        except ResolveNotRunning:
            return json.dumps({
                "error": "DaVinci Resolve is not running.",
                "name": None,
            })
        except Exception as exc:
            return json.dumps({"error": str(exc)})
