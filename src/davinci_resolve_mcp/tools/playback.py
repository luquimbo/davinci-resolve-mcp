"""Playback, page navigation, timecode, and version tools.

Provides read/write access to the Resolve playhead (timecode, current item)
and global info (version, product name, current page).  These are lightweight
calls that don't mutate project data, except for page switching and timecode
seeking.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..constants import ResolvePage
from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI

# Derive valid pages from the ResolvePage enum so they stay in sync automatically
_VALID_PAGES = {p.value for p in ResolvePage}


def register(mcp: FastMCP) -> None:
    """Register all playback / navigation / version tools on *mcp*."""

    # ------------------------------------------------------------------
    # Page navigation
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def playback_get_page() -> str:
        """Return the name of the currently active Resolve page.

        Possible values: "media", "cut", "edit", "fusion", "color",
        "fairlight", "deliver", or "" if Resolve cannot determine the page.
        """
        try:
            api = ResolveAPI.get_instance()
            # GetCurrentPage() returns a lowercase string like "edit"
            page: str = api.resolve.GetCurrentPage() or ""
            return page
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            # Stale scripting bridge reference — Resolve may have restarted
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("playback_get_page", str(exc)) from exc

    @mcp.tool()
    def playback_open_page(page: str) -> bool:
        """Switch Resolve to a different workspace page.

        Args:
            page: Target page name.  Must be one of: media, cut, edit,
                  fusion, color, fairlight, deliver.

        Returns:
            True if the page switch succeeded.
        """
        # Validate before hitting the API to give a clear error message
        page_lower = page.strip().lower()
        if page_lower not in _VALID_PAGES:
            raise ResolveOperationFailed(
                "playback_open_page",
                f"Invalid page '{page}'. Valid pages: {', '.join(sorted(_VALID_PAGES))}",
            )

        try:
            api = ResolveAPI.get_instance()
            # OpenPage() returns True on success, False on failure
            result: bool = api.resolve.OpenPage(page_lower)
            if not result:
                raise ResolveOperationFailed(
                    "playback_open_page",
                    f"Resolve refused to switch to page '{page_lower}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("playback_open_page", str(exc)) from exc

    # ------------------------------------------------------------------
    # Timecode
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def playback_get_timecode() -> str:
        """Return the current playhead timecode (e.g. "01:00:05:12").

        Requires an open project with at least one timeline.
        """
        try:
            api = ResolveAPI.get_instance()
            timeline = api.timeline
            if timeline is None:
                raise ResolveOperationFailed(
                    "playback_get_timecode",
                    "No timeline is currently open.",
                )
            # GetCurrentTimecode() returns a timecode string like "01:00:00:00"
            timecode: str = timeline.GetCurrentTimecode()
            return timecode
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("playback_get_timecode", str(exc)) from exc

    @mcp.tool()
    def playback_set_timecode(timecode: str) -> bool:
        """Move the playhead to a specific timecode position.

        Args:
            timecode: Target timecode string, e.g. "01:00:05:12".
                      Must match the project's timecode format.

        Returns:
            True if the playhead was moved successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            timeline = api.timeline
            if timeline is None:
                raise ResolveOperationFailed(
                    "playback_set_timecode",
                    "No timeline is currently open.",
                )
            # SetCurrentTimecode() returns True on success
            result: bool = timeline.SetCurrentTimecode(timecode)
            if not result:
                raise ResolveOperationFailed(
                    "playback_set_timecode",
                    f"Resolve could not seek to timecode '{timecode}'. "
                    "Verify the format matches the project settings.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("playback_set_timecode", str(exc)) from exc

    # ------------------------------------------------------------------
    # Current timeline item
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def playback_get_current_item() -> dict | None:
        """Return info about the timeline item under the playhead, or None.

        Returns a dict with keys: name, start, end, duration.
        Returns None if no item is under the playhead or no timeline is open.
        """
        try:
            api = ResolveAPI.get_instance()
            timeline = api.timeline
            if timeline is None:
                return None

            # GetCurrentVideoItem() returns the clip under the playhead or None
            item = timeline.GetCurrentVideoItem()
            if item is None:
                return None

            return {
                "name": item.GetName(),
                "start": item.GetStart(),
                "end": item.GetEnd(),
                "duration": item.GetDuration(),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "playback_get_current_item", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Resolve version / product info
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def resolve_get_version() -> str:
        """Return the DaVinci Resolve version as a dotted string (e.g. "19.1.2").

        The underlying API may return a list of version components or a string;
        this tool always returns a single joined string.
        """
        try:
            api = ResolveAPI.get_instance()
            # GetVersion() may return a string or a list like [19, 1, 2, 0]
            raw = api.resolve.GetVersion()
            if isinstance(raw, (list, tuple)):
                return ".".join(str(part) for part in raw)
            return str(raw)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("resolve_get_version", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def resolve_get_product() -> str:
        """Return the Resolve product name.

        Typically "DaVinci Resolve" (free) or "DaVinci Resolve Studio" (paid).
        """
        try:
            api = ResolveAPI.get_instance()
            name: str = api.resolve.GetProductName()
            return name
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("resolve_get_product", str(exc)) from exc
