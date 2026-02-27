"""MCP Resource: resolve://system — version, current page, product name."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from ..resolve_api import ResolveAPI
from ..exceptions import ResolveNotRunning


def register(mcp: FastMCP) -> None:
    """Register the resolve://system resource."""

    @mcp.resource("resolve://system")
    def system_info() -> str:
        """Current DaVinci Resolve system information.

        Returns JSON with:
        - version: Resolve version string (e.g. "19.1.2")
        - product: "DaVinci Resolve" or "DaVinci Resolve Studio"
        - current_page: Active workspace page name
        """
        try:
            api = ResolveAPI.get_instance()
            resolve = api.resolve

            # Version may come back as a list of ints or a string
            raw_version = resolve.GetVersion()
            if isinstance(raw_version, (list, tuple)):
                version = ".".join(str(v) for v in raw_version)
            else:
                version = str(raw_version)

            return json.dumps({
                "version": version,
                "product": resolve.GetProductName() or "DaVinci Resolve",
                "current_page": resolve.GetCurrentPage() or "unknown",
            })
        except ResolveNotRunning:
            return json.dumps({
                "error": "DaVinci Resolve is not running.",
                "version": None,
                "product": None,
                "current_page": None,
            })
        except Exception as exc:
            return json.dumps({"error": str(exc)})
