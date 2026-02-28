"""Shared helpers used by multiple tool modules.

Consolidates duplicated utility functions (require_timeline, require_media_pool,
find_item) and the VALID_TRACK_TYPES constant that were previously copy-pasted
across color.py, fusion.py, timeline_item.py, and timeline.py.
"""

from __future__ import annotations

from typing import Any

from ..constants import TrackType
from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI

# Canonical set derived from the TrackType enum so it stays in sync automatically.
VALID_TRACK_TYPES = {t.value for t in TrackType}


def require_timeline() -> Any:
    """Return the current timeline or raise if none is open.

    Centralises the repeated "get API -> get timeline -> None check"
    boilerplate so each tool doesn't have to duplicate it.
    """
    api = ResolveAPI.get_instance()
    timeline = api.timeline
    if timeline is None:
        raise ResolveOperationFailed(
            "require_timeline",
            "No timeline is currently open.",
        )
    return timeline


def require_media_pool() -> Any:
    """Return the MediaPool object or raise if unavailable.

    Used by tools that operate on the media pool (e.g. inserting generators
    or titles) rather than on individual timeline items.
    """
    api = ResolveAPI.get_instance()
    pool = api.media_pool
    if pool is None:
        raise ResolveOperationFailed(
            "require_media_pool",
            "Media Pool is not available. Is a project open?",
        )
    return pool


def find_item(
    name: str,
    track_type: str = "video",
    track_index: int = 1,
) -> Any:
    """Locate a timeline item by name on the specified track.

    Uses the most defensive version with an AttributeError guard on each item
    to skip stale or invalid item references.  Validates track_type and
    track_index before calling the Resolve API.

    Args:
        name:        Exact display name of the timeline item.
        track_type:  Track type -- "video", "audio", or "subtitle".
        track_index: 1-based track number within the track type.

    Returns:
        The first TimelineItem whose GetName() matches *name*.

    Raises:
        ResolveOperationFailed: If the track type is invalid, the track
            is empty, or no item matches the given name.
    """
    # Validate track_type before hitting the API to give a clear error
    if track_type not in VALID_TRACK_TYPES:
        raise ResolveOperationFailed(
            "find_item",
            f"Invalid track_type '{track_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_TRACK_TYPES))}.",
        )

    # Validate track_index is a positive integer (1-based indexing)
    if track_index < 1:
        raise ResolveOperationFailed(
            "find_item",
            f"track_index must be >= 1, got {track_index}.",
        )

    timeline = require_timeline()

    # GetItemListInTrack() returns a list of TimelineItem objects or None
    items = timeline.GetItemListInTrack(track_type, track_index)
    if not items:
        raise ResolveOperationFailed(
            "find_item",
            f"Track '{track_type}' index {track_index} has no items. "
            f"Cannot find '{name}'.",
        )

    # Linear scan with AttributeError guard for stale item references
    for item in items:
        try:
            if item.GetName() == name:
                return item
        except AttributeError:
            # Skip stale or invalid item references
            continue

    raise ResolveOperationFailed(
        "find_item",
        f"Item '{name}' not found on {track_type} track {track_index}.",
    )
