"""Timeline tools — CRUD, tracks, items, markers, and clip operations.

Provides full control over DaVinci Resolve timelines: querying and switching the
current timeline, renaming, inspecting frame ranges, managing video/audio/subtitle
tracks (add, delete, rename, enable, lock), listing items within tracks with
pagination, appending and deleting clips, duplicating timelines, and managing
frame markers.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


def register(mcp: FastMCP) -> None:
    """Register all timeline tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # Timeline querying and switching
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_current() -> dict | None:
        """Return info about the current timeline, or None if no timeline is open.

        Returns a dict with keys: name, start_frame, end_frame,
        video_tracks, audio_tracks, start_timecode.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                return None

            return {
                "name": tl.GetName(),
                "start_frame": tl.GetStartFrame(),
                "end_frame": tl.GetEndFrame(),
                "video_tracks": tl.GetTrackCount("video"),
                "audio_tracks": tl.GetTrackCount("audio"),
                "start_timecode": tl.GetStartTimecode(),
            }
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading current timeline."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_current", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_set_current(name: str) -> bool:
        """Set the current timeline by name.

        Args:
            name: Exact name of the timeline to activate.  Searches all
                  timelines in the current project by index.

        Returns:
            True if the timeline was found and set as current.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "timeline_set_current", "No project is currently open."
                )

            # Iterate through all timelines to find the one with a matching name.
            # GetTimelineByIndex() uses 1-based indexing.
            count: int = project.GetTimelineCount()
            for i in range(1, count + 1):
                tl = project.GetTimelineByIndex(i)
                if tl is not None and tl.GetName() == name:
                    result: bool = project.SetCurrentTimeline(tl)
                    if not result:
                        raise ResolveOperationFailed(
                            "timeline_set_current",
                            f"Resolve refused to switch to timeline '{name}'.",
                        )
                    return True

            raise ResolveOperationFailed(
                "timeline_set_current",
                f"No timeline named '{name}' found in the current project.",
            )
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while setting current timeline."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_set_current", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_count() -> int:
        """Return the number of timelines in the current project."""
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "timeline_get_count", "No project is currently open."
                )
            return project.GetTimelineCount()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while counting timelines."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_count", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_by_index(index: int) -> dict | None:
        """Return info about a timeline at the given 1-based index.

        Args:
            index: 1-based position of the timeline in the project.

        Returns:
            A dict with keys: name, start_frame, end_frame,
            video_tracks, audio_tracks, start_timecode.
            None if no timeline exists at the given index.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "timeline_get_by_index", "No project is currently open."
                )

            # GetTimelineByIndex() uses 1-based indexing; returns None if invalid
            tl = project.GetTimelineByIndex(index)
            if tl is None:
                return None

            return {
                "name": tl.GetName(),
                "start_frame": tl.GetStartFrame(),
                "end_frame": tl.GetEndFrame(),
                "video_tracks": tl.GetTrackCount("video"),
                "audio_tracks": tl.GetTrackCount("audio"),
                "start_timecode": tl.GetStartTimecode(),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading timeline by index."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_by_index", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Timeline name
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_name() -> str:
        """Return the name of the current timeline.

        Raises an error if no timeline is open.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_name", "No timeline is currently open."
                )
            return tl.GetName()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading timeline name."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_name", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_set_name(name: str) -> bool:
        """Rename the current timeline.

        Args:
            name: The new name for the current timeline.

        Returns:
            True if the rename succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_set_name", "No timeline is currently open."
                )
            # SetName() returns True on success
            result: bool = tl.SetName(name)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_set_name",
                    f"Resolve refused to rename timeline to '{name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while renaming timeline."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_set_name", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Frame range
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_start_frame() -> int:
        """Return the start frame number of the current timeline."""
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_start_frame", "No timeline is currently open."
                )
            return tl.GetStartFrame()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading start frame."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_start_frame", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_end_frame() -> int:
        """Return the end frame number of the current timeline."""
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_end_frame", "No timeline is currently open."
                )
            return tl.GetEndFrame()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading end frame."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_end_frame", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Track management (count, add, delete, name, enable, lock)
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_track_count(track_type: str = "video") -> int:
        """Return the number of tracks of the given type in the current timeline.

        Args:
            track_type: One of "video", "audio", or "subtitle".
                        Defaults to "video".
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_track_count", "No timeline is currently open."
                )
            return tl.GetTrackCount(track_type)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while counting tracks."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_track_count", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_add_track(track_type: str, count: int = 1) -> bool:
        """Add one or more tracks to the current timeline.

        Args:
            track_type: Type of track to add: "video", "audio", or "subtitle".
            count: Number of tracks to add (default 1).  Each call to the
                   Resolve API adds a single track, so this repeats the call.

        Returns:
            True if all requested tracks were added successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_add_track", "No timeline is currently open."
                )

            # AddTrack() adds one track per call; repeat for the requested count
            for i in range(count):
                result: bool = tl.AddTrack(track_type)
                if not result:
                    raise ResolveOperationFailed(
                        "timeline_add_track",
                        f"Failed to add {track_type} track (attempt {i + 1} of {count}).",
                    )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while adding track."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_add_track", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_delete_track(track_type: str, track_index: int) -> bool:
        """Delete a track from the current timeline.

        Args:
            track_type: Type of track: "video", "audio", or "subtitle".
            track_index: 1-based index of the track to delete.

        Returns:
            True if the track was deleted.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_delete_track", "No timeline is currently open."
                )
            # DeleteTrack() returns True on success
            result: bool = tl.DeleteTrack(track_type, track_index)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_delete_track",
                    f"Could not delete {track_type} track {track_index}. "
                    "Verify the track type and index are valid.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while deleting track."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_delete_track", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_track_name(track_type: str, track_index: int) -> str:
        """Return the name of a specific track in the current timeline.

        Args:
            track_type: One of "video", "audio", or "subtitle".
            track_index: 1-based index of the track.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_track_name", "No timeline is currently open."
                )
            # GetTrackName() returns the track's display name
            return tl.GetTrackName(track_type, track_index)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading track name."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_track_name", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_set_track_name(track_type: str, track_index: int, name: str) -> bool:
        """Rename a track in the current timeline.

        Args:
            track_type: One of "video", "audio", or "subtitle".
            track_index: 1-based index of the track.
            name: The new display name for the track.

        Returns:
            True if the rename succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_set_track_name", "No timeline is currently open."
                )
            result: bool = tl.SetTrackName(track_type, track_index, name)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_set_track_name",
                    f"Resolve refused to rename {track_type} track {track_index} "
                    f"to '{name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while renaming track."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_set_track_name", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_set_track_enabled(
        track_type: str, track_index: int, enabled: bool
    ) -> bool:
        """Enable or disable a track in the current timeline.

        Args:
            track_type: One of "video", "audio", or "subtitle".
            track_index: 1-based index of the track.
            enabled: True to enable, False to disable the track.

        Returns:
            True if the operation succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_set_track_enabled", "No timeline is currently open."
                )
            # SetTrackEnable() takes (track_type, index, bool)
            result: bool = tl.SetTrackEnable(track_type, track_index, enabled)
            if not result:
                state = "enable" if enabled else "disable"
                raise ResolveOperationFailed(
                    "timeline_set_track_enabled",
                    f"Could not {state} {track_type} track {track_index}.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while toggling track enabled state."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_set_track_enabled", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_set_track_locked(
        track_type: str, track_index: int, locked: bool
    ) -> bool:
        """Lock or unlock a track in the current timeline.

        Args:
            track_type: One of "video", "audio", or "subtitle".
            track_index: 1-based index of the track.
            locked: True to lock the track, False to unlock it.

        Returns:
            True if the operation succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_set_track_locked", "No timeline is currently open."
                )
            # SetTrackLock() takes (track_type, index, bool)
            result: bool = tl.SetTrackLock(track_type, track_index, locked)
            if not result:
                state = "lock" if locked else "unlock"
                raise ResolveOperationFailed(
                    "timeline_set_track_locked",
                    f"Could not {state} {track_type} track {track_index}.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while toggling track lock state."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_set_track_locked", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Timeline items (clips on tracks)
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_items_in_track(
        track_type: str, track_index: int, offset: int = 0, limit: int = 50
    ) -> dict:
        """List timeline items on a specific track with pagination.

        Args:
            track_type: One of "video", "audio", or "subtitle".
            track_index: 1-based index of the track.
            offset: Number of items to skip from the start (default 0).
            limit: Maximum number of items to return (default 50).

        Returns:
            A dict with keys: items (list of {name, start, end, duration}),
            total, offset, limit, has_more.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_items_in_track",
                    "No timeline is currently open.",
                )

            # GetItemListInTrack() returns all items on the specified track
            all_items = tl.GetItemListInTrack(track_type, track_index)
            if not all_items:
                return {
                    "items": [],
                    "total": 0,
                    "offset": offset,
                    "limit": limit,
                    "has_more": False,
                }

            total = len(all_items)
            # Apply pagination: slice the full list by offset and limit
            page = all_items[offset : offset + limit]

            items = []
            for item in page:
                items.append({
                    "name": item.GetName(),
                    "start": item.GetStart(),
                    "end": item.GetEnd(),
                    "duration": item.GetDuration(),
                })

            return {
                "items": items,
                "total": total,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + limit) < total,
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while listing track items."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_items_in_track", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Clip operations (append, delete)
    # ------------------------------------------------------------------

    @mcp.tool()
    def timeline_append_clips(clip_names: list[str]) -> bool:
        """Append media pool clips to the end of the current timeline.

        Searches the media pool's current folder for clips matching the
        given names, then appends them in order.

        Args:
            clip_names: List of clip names (as shown in the media pool)
                        to append to the timeline.

        Returns:
            True if the clips were appended successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            pool = api.media_pool
            if pool is None:
                raise ResolveOperationFailed(
                    "timeline_append_clips",
                    "No project or media pool is available.",
                )

            # Get clips from the current media pool folder
            folder = pool.GetCurrentFolder()
            if folder is None:
                raise ResolveOperationFailed(
                    "timeline_append_clips",
                    "Could not access the current media pool folder.",
                )

            # GetClipList() returns all clips in the current folder
            all_clips = folder.GetClipList()
            if not all_clips:
                raise ResolveOperationFailed(
                    "timeline_append_clips",
                    "The current media pool folder is empty.",
                )

            # Build a lookup by name, then collect matching clips in request order
            clip_lookup: dict = {}
            for clip in all_clips:
                clip_lookup[clip.GetName()] = clip

            clip_objs = []
            missing = []
            for name in clip_names:
                if name in clip_lookup:
                    clip_objs.append(clip_lookup[name])
                else:
                    missing.append(name)

            if missing:
                raise ResolveOperationFailed(
                    "timeline_append_clips",
                    f"Clips not found in current folder: {', '.join(missing)}",
                )

            # AppendToTimeline() accepts a list of MediaPoolItem objects
            result = pool.AppendToTimeline(clip_objs)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_append_clips",
                    "Resolve failed to append clips to the timeline.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while appending clips."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_append_clips", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_delete_clips(
        item_names: list[str],
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Delete timeline items by name from a specific track.

        Args:
            item_names: Names of the timeline items to delete.
            track_type: Type of track to search: "video", "audio", or "subtitle".
                        Defaults to "video".
            track_index: 1-based index of the track to search (default 1).

        Returns:
            True if the items were deleted.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_delete_clips", "No timeline is currently open."
                )

            # Get all items on the specified track
            all_items = tl.GetItemListInTrack(track_type, track_index)
            if not all_items:
                raise ResolveOperationFailed(
                    "timeline_delete_clips",
                    f"No items found on {track_type} track {track_index}.",
                )

            # Collect items whose names match the requested deletion list
            names_set = set(item_names)
            items_to_delete = [
                item for item in all_items if item.GetName() in names_set
            ]

            if not items_to_delete:
                raise ResolveOperationFailed(
                    "timeline_delete_clips",
                    f"None of the specified items were found on "
                    f"{track_type} track {track_index}.",
                )

            # DeleteClips() takes a list of TimelineItem objects
            result: bool = tl.DeleteClips(items_to_delete)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_delete_clips",
                    "Resolve failed to delete the specified clips.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while deleting clips."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_delete_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Timeline duplication
    # ------------------------------------------------------------------

    @mcp.tool()
    def timeline_duplicate() -> str | None:
        """Duplicate the current timeline.

        Returns:
            The name of the newly created timeline, or None if duplication
            failed.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_duplicate", "No timeline is currently open."
                )

            # DuplicateTimeline() returns a new Timeline object or None
            new_tl = tl.DuplicateTimeline()
            if new_tl is None:
                return None

            return new_tl.GetName()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while duplicating timeline."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_duplicate", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Markers
    # ------------------------------------------------------------------

    @mcp.tool()
    def timeline_add_marker(
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        """Add a marker to the current timeline at a specific frame.

        Args:
            frame_id: Frame number where the marker should be placed.
            color: Marker color.  Standard Resolve colors include "Blue",
                   "Cyan", "Green", "Yellow", "Red", "Pink", "Purple",
                   "Fuchsia", "Rose", "Lavender", "Sky", "Mint", "Lemon",
                   "Sand", "Cocoa", "Cream".
            name: Optional marker name/title.
            note: Optional marker note/description.
            duration: Marker duration in frames (default 1).
            custom_data: Optional custom data string for the marker.

        Returns:
            True if the marker was added.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_add_marker", "No timeline is currently open."
                )

            # AddMarker(frameId, color, name, note, duration, customData)
            result: bool = tl.AddMarker(
                frame_id, color, name, note, duration, custom_data
            )
            if not result:
                raise ResolveOperationFailed(
                    "timeline_add_marker",
                    f"Could not add marker at frame {frame_id}. "
                    "A marker may already exist at that frame.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while adding marker."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_add_marker", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def timeline_get_markers() -> dict:
        """Return all markers on the current timeline.

        Returns:
            A dict mapping frame numbers (as string keys) to marker info dicts.
            Each marker dict contains: color, duration, note, name, customData.
            Returns an empty dict if no markers exist or no timeline is open.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_get_markers", "No timeline is currently open."
                )

            # GetMarkers() returns {frameId: {color, duration, note, name, customData}}
            markers = tl.GetMarkers()
            return markers if markers else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading markers."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_get_markers", str(exc)
            ) from exc

    @mcp.tool()
    def timeline_delete_marker(frame_id: int) -> bool:
        """Delete a marker at a specific frame on the current timeline.

        Args:
            frame_id: Frame number of the marker to delete.

        Returns:
            True if the marker was deleted.
        """
        try:
            api = ResolveAPI.get_instance()
            tl = api.timeline
            if tl is None:
                raise ResolveOperationFailed(
                    "timeline_delete_marker", "No timeline is currently open."
                )

            # DeleteMarkerAtFrame() returns True on success
            result: bool = tl.DeleteMarkerAtFrame(frame_id)
            if not result:
                raise ResolveOperationFailed(
                    "timeline_delete_marker",
                    f"No marker found at frame {frame_id}, or deletion failed.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while deleting marker."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "timeline_delete_marker", str(exc)
            ) from exc
