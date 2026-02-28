"""Timeline-item tools — transform, crop, composite, color, flags, and markers.

Provides 18 tools to inspect and modify items (clips) on a timeline track.
Items are identified by display name, track type, and track index.  A module-level
helper resolves the matching TimelineItem object from the active timeline.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI

# Valid track types accepted by the Resolve scripting API
_VALID_TRACK_TYPES = {"video", "audio", "subtitle"}


# ------------------------------------------------------------------
# Helper — resolve a timeline item from name + track coordinates
# ------------------------------------------------------------------

def _find_item(
    name: str,
    track_type: str = "video",
    track_index: int = 1,
) -> Any:
    """Locate a timeline item by name on the specified track.

    Iterates through GetItemListInTrack() for the given track type and index,
    returning the first item whose GetName() matches *name*.

    Args:
        name:        Display name of the timeline item.
        track_type:  "video", "audio", or "subtitle" (Resolve track type string).
        track_index: 1-based track number.

    Raises:
        ResolveOperationFailed: If no timeline is open, the track is empty,
            or no item matches the given name.
    """
    # Validate track_type before hitting the API to give a clear error
    if track_type not in _VALID_TRACK_TYPES:
        raise ResolveOperationFailed(
            "_find_item",
            f"Invalid track_type '{track_type}'. Must be one of: {', '.join(sorted(_VALID_TRACK_TYPES))}",
        )

    # Validate track_index is a positive integer (1-based indexing)
    if track_index < 1:
        raise ResolveOperationFailed("_find_item", "track_index must be >= 1 (1-based indexing).")

    api = ResolveAPI.get_instance()
    timeline = api.timeline
    if timeline is None:
        raise ResolveOperationFailed(
            "_find_item",
            "No timeline is currently open.",
        )

    # GetItemListInTrack() returns a list of TimelineItem objects
    items = timeline.GetItemListInTrack(track_type, track_index)
    if not items:
        raise ResolveOperationFailed(
            "_find_item",
            f"Track '{track_type}' index {track_index} has no items. "
            f"Cannot find '{name}'.",
        )

    # Linear scan — timeline tracks are typically manageable in size
    for item in items:
        try:
            if item.GetName() == name:
                return item
        except AttributeError:
            # Skip stale or invalid item references
            continue

    raise ResolveOperationFailed(
        "_find_item",
        f"Item '{name}' not found on {track_type} track {track_index}.",
    )


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all timeline-item tools on *mcp*."""

    # ==============================================================
    # Basic info
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_name(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> str:
        """Return the display name of a timeline item.

        Args:
            item_name:   Name of the item to look up.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            return item.GetName()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_name", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_duration(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> int:
        """Return the duration of a timeline item in frames.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            return int(item.GetDuration())
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_duration", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_start_end(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict:
        """Return the start frame, end frame, and duration of a timeline item.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            Dict with keys: start, end, duration (all integers in frames).
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            return {
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
            raise ResolveOperationFailed("item_get_start_end", str(exc)) from exc

    # ==============================================================
    # Properties
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_properties(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict:
        """Return all properties of a timeline item as key-value pairs.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            Dict of property keys and values (e.g. "ZoomX", "Pan", "Opacity").
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # GetProperty() with no args returns the full property dict
            props = item.GetProperty()
            return props if isinstance(props, dict) else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_properties", str(exc)) from exc

    @mcp.tool()
    def item_set_property(
        item_name: str,
        key: str,
        value: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set a single property on a timeline item.

        Args:
            item_name:   Name of the item.
            key:         Property key (e.g. "ZoomX", "Pan", "Opacity").
            value:       Value to assign as a string.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the property was set successfully.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.SetProperty(key, value)
            if not result:
                raise ResolveOperationFailed(
                    "item_set_property",
                    f"Failed to set '{key}' on item '{item_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_property", str(exc)) from exc

    # ==============================================================
    # Transform
    # ==============================================================

    @mcp.tool()
    def item_set_transform(
        item_name: str,
        zoom_x: float | None = None,
        zoom_y: float | None = None,
        position_x: float | None = None,
        position_y: float | None = None,
        rotation: float | None = None,
        anchor_x: float | None = None,
        anchor_y: float | None = None,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set transform properties (zoom, position, rotation, anchor) on an item.

        Only non-None parameters are applied; the rest remain unchanged.

        Args:
            item_name:   Name of the item.
            zoom_x:      Horizontal zoom factor (1.0 = 100%).
            zoom_y:      Vertical zoom factor (1.0 = 100%).
            position_x:  Horizontal pan offset in pixels.
            position_y:  Vertical tilt offset in pixels.
            rotation:    Rotation angle in degrees.
            anchor_x:    Anchor point X coordinate.
            anchor_y:    Anchor point Y coordinate.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if all provided transforms were applied.
        """
        # Map friendly param names to Resolve property keys
        param_map: list[tuple[str, float | None]] = [
            ("ZoomX", zoom_x),
            ("ZoomY", zoom_y),
            ("Pan", position_x),
            ("Tilt", position_y),
            ("RotationAngle", rotation),
            ("AnchorPointX", anchor_x),
            ("AnchorPointY", anchor_y),
        ]

        try:
            item = _find_item(item_name, track_type, track_index)

            applied = 0
            for key, value in param_map:
                if value is not None:
                    # SetProperty expects the value; Resolve handles numeric coercion
                    ok: bool = item.SetProperty(key, value)
                    if not ok:
                        raise ResolveOperationFailed(
                            "item_set_transform",
                            f"Failed to set '{key}' = {value} on item '{item_name}'.",
                        )
                    applied += 1

            if applied == 0:
                raise ResolveOperationFailed(
                    "item_set_transform",
                    "No transform parameters provided. Supply at least one.",
                )

            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_transform", str(exc)) from exc

    # ==============================================================
    # Crop
    # ==============================================================

    @mcp.tool()
    def item_set_crop(
        item_name: str,
        left: float | None = None,
        right: float | None = None,
        top: float | None = None,
        bottom: float | None = None,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set crop values on a timeline item.

        Only non-None parameters are applied; the rest remain unchanged.

        Args:
            item_name:   Name of the item.
            left:        Left crop value.
            right:       Right crop value.
            top:         Top crop value.
            bottom:      Bottom crop value.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if all provided crop values were applied.
        """
        param_map: list[tuple[str, float | None]] = [
            ("CropLeft", left),
            ("CropRight", right),
            ("CropTop", top),
            ("CropBottom", bottom),
        ]

        try:
            item = _find_item(item_name, track_type, track_index)

            applied = 0
            for key, value in param_map:
                if value is not None:
                    ok: bool = item.SetProperty(key, value)
                    if not ok:
                        raise ResolveOperationFailed(
                            "item_set_crop",
                            f"Failed to set '{key}' = {value} on item '{item_name}'.",
                        )
                    applied += 1

            if applied == 0:
                raise ResolveOperationFailed(
                    "item_set_crop",
                    "No crop parameters provided. Supply at least one.",
                )

            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_crop", str(exc)) from exc

    # ==============================================================
    # Composite
    # ==============================================================

    @mcp.tool()
    def item_set_composite(
        item_name: str,
        mode: str | None = None,
        opacity: float | None = None,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set composite mode and/or opacity on a timeline item.

        Args:
            item_name:   Name of the item.
            mode:        Composite/blend mode name (e.g. "Normal", "Add",
                         "Multiply", "Screen", "Overlay").
            opacity:     Opacity value from 0 (transparent) to 100 (opaque).
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the composite settings were applied.
        """
        try:
            item = _find_item(item_name, track_type, track_index)

            applied = 0

            if mode is not None:
                ok: bool = item.SetProperty("CompositeMode", mode)
                if not ok:
                    raise ResolveOperationFailed(
                        "item_set_composite",
                        f"Failed to set CompositeMode '{mode}' on item '{item_name}'.",
                    )
                applied += 1

            if opacity is not None:
                ok = item.SetProperty("Opacity", opacity)
                if not ok:
                    raise ResolveOperationFailed(
                        "item_set_composite",
                        f"Failed to set Opacity {opacity} on item '{item_name}'.",
                    )
                applied += 1

            if applied == 0:
                raise ResolveOperationFailed(
                    "item_set_composite",
                    "No composite parameters provided. Supply mode, opacity, or both.",
                )

            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_composite", str(exc)) from exc

    # ==============================================================
    # Color label
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_color(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> str:
        """Return the label color assigned to a timeline item.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            Color name string, or empty string if none is set.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            color: str = item.GetClipColor() or ""
            return color
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_color", str(exc)) from exc

    @mcp.tool()
    def item_set_color(
        item_name: str,
        color: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set the label color on a timeline item.

        Args:
            item_name:   Name of the item.
            color:       Color name (e.g. "Orange", "Blue", "Green").
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the color was applied.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.SetClipColor(color)
            if not result:
                raise ResolveOperationFailed(
                    "item_set_color",
                    f"Failed to set color '{color}' on item '{item_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_color", str(exc)) from exc

    # ==============================================================
    # Enable / disable
    # ==============================================================

    @mcp.tool()
    def item_set_enabled(
        item_name: str,
        enabled: bool,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Enable or disable a timeline item (muted/unmuted).

        Args:
            item_name:   Name of the item.
            enabled:     True to enable, False to disable (mute).
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the state was changed.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.SetClipEnabled(enabled)
            if not result:
                state = "enable" if enabled else "disable"
                raise ResolveOperationFailed(
                    "item_set_enabled",
                    f"Failed to {state} item '{item_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_set_enabled", str(exc)) from exc

    # ==============================================================
    # Markers
    # ==============================================================

    @mcp.tool()
    def item_add_marker(
        item_name: str,
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Add a marker to a timeline item at a given frame offset.

        Args:
            item_name:   Name of the item.
            frame_id:    Frame offset from the item's start for the marker.
            color:       Marker color (e.g. "Blue", "Red", "Green").
            name:        Optional short label for the marker.
            note:        Optional longer note attached to the marker.
            duration:    Marker duration in frames (default 1).
            custom_data: Optional custom-data string stored with the marker.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the marker was added.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.AddMarker(
                frame_id, color, name, note, duration, custom_data,
            )
            if not result:
                raise ResolveOperationFailed(
                    "item_add_marker",
                    f"Failed to add marker at frame {frame_id} on item '{item_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_add_marker", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_markers(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict:
        """Return all markers on a timeline item. Keys are frame offsets.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            Dict mapping frame offset to marker info dict with keys:
            color, name, note, duration, customData.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            markers = item.GetMarkers()
            return markers if isinstance(markers, dict) else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_markers", str(exc)) from exc

    @mcp.tool()
    def item_delete_marker(
        item_name: str,
        frame_id: int,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Delete the marker at a specific frame offset on a timeline item.

        Args:
            item_name:   Name of the item.
            frame_id:    Frame offset of the marker to remove.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the marker was deleted.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.DeleteMarkerAtFrame(frame_id)
            if not result:
                raise ResolveOperationFailed(
                    "item_delete_marker",
                    f"No marker at frame {frame_id} on item '{item_name}', "
                    "or Resolve refused the deletion.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_delete_marker", str(exc)) from exc

    # ==============================================================
    # Flags
    # ==============================================================

    @mcp.tool()
    def item_add_flag(
        item_name: str,
        color: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Add a flag of the given color to a timeline item.

        Args:
            item_name:   Name of the item.
            color:       Flag color (e.g. "Blue", "Red", "Green").
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            True if the flag was added.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            result: bool = item.AddFlag(color)
            if not result:
                raise ResolveOperationFailed(
                    "item_add_flag",
                    f"Failed to add '{color}' flag on item '{item_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_add_flag", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_flags(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> list[str]:
        """Return all flag colors currently set on a timeline item.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            List of color name strings (e.g. ["Blue", "Red"]).
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            flags = item.GetFlagList()
            return list(flags) if flags else []
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("item_get_flags", str(exc)) from exc

    # ==============================================================
    # Related items
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_media_pool_item(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict | None:
        """Return the source media-pool clip for a timeline item, if available.

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            Dict with "name" and "file_path" keys, or None if no source clip
            is linked (e.g. for generators or titles).
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            mpi = item.GetMediaPoolItem()
            if mpi is None:
                return None
            return {
                "name": mpi.GetName(),
                "file_path": mpi.GetClipProperty("File Path"),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "item_get_media_pool_item", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def item_get_linked_items(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> list[dict]:
        """Return items linked to this timeline item (e.g. audio for a video clip).

        Args:
            item_name:   Name of the item.
            track_type:  Track type — "video" or "audio".
            track_index: 1-based track number.

        Returns:
            List of dicts, each with a "name" key. Empty list if no linked items.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            linked = item.GetLinkedItems()
            if not linked:
                return []
            # Build a summary for each linked item
            return [{"name": li.GetName()} for li in linked]
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "item_get_linked_items", str(exc)
            ) from exc
