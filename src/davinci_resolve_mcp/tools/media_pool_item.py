"""Media-pool clip tools — metadata, markers, flags, proxy, and properties.

Provides 16 tools to inspect and modify clips in the current media-pool folder.
Clips are identified by display name; a module-level helper searches the active
folder's clip list so every tool receives a resolved Resolve MediaPoolItem object.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


# ------------------------------------------------------------------
# Helper — resolve a clip object from its display name
# ------------------------------------------------------------------

def _find_clip(name: str) -> Any:
    """Search the current media-pool folder for a clip matching *name*.

    Iterates through GetClipList() on the active folder and returns the
    first clip whose GetName() matches.  Raises ResolveOperationFailed
    if no match is found or no media pool / folder is available.
    """
    api = ResolveAPI.get_instance()
    media_pool = api.media_pool
    if media_pool is None:
        raise ResolveOperationFailed(
            "_find_clip",
            "No media pool available. Is a project open?",
        )

    # GetCurrentFolder() returns the folder currently shown in the media pool
    folder = media_pool.GetCurrentFolder()
    if folder is None:
        raise ResolveOperationFailed(
            "_find_clip",
            "No current folder in the media pool.",
        )

    clips = folder.GetClipList()
    if not clips:
        raise ResolveOperationFailed(
            "_find_clip",
            f"Current folder has no clips. Cannot find '{name}'.",
        )

    # Linear scan — clip lists are typically small enough for this
    for clip in clips:
        try:
            if clip.GetName() == name:
                return clip
        except AttributeError:
            # Skip any stale or invalid clip references
            continue

    raise ResolveOperationFailed(
        "_find_clip",
        f"Clip '{name}' not found in the current media-pool folder.",
    )


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all media-pool clip tools on *mcp*."""

    # ==============================================================
    # Name
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_name(clip_name: str) -> str:
        """Return the display name of a media-pool clip.

        Args:
            clip_name: Current name of the clip to look up.
        """
        try:
            clip = _find_clip(clip_name)
            return clip.GetName()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip name."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_name", str(exc)) from exc

    @mcp.tool()
    def clip_set_name(clip_name: str, new_name: str) -> bool:
        """Rename a media-pool clip.

        Args:
            clip_name: Current name of the clip.
            new_name:  Desired new display name.

        Returns:
            True if the rename succeeded.
        """
        try:
            clip = _find_clip(clip_name)
            # SetClipProperty with "Clip Name" is the rename mechanism
            result: bool = clip.SetClipProperty("Clip Name", new_name)
            if not result:
                raise ResolveOperationFailed(
                    "clip_set_name",
                    f"Resolve refused to rename '{clip_name}' to '{new_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while renaming clip."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_set_name", str(exc)) from exc

    # ==============================================================
    # Metadata
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_metadata(clip_name: str) -> dict:
        """Return all metadata fields for a clip as key-value pairs.

        Args:
            clip_name: Name of the clip to inspect.

        Returns:
            Dict of metadata keys and their string values.
        """
        try:
            clip = _find_clip(clip_name)
            # GetMetadata() with no args returns the full dict
            metadata = clip.GetMetadata()
            return metadata if isinstance(metadata, dict) else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip metadata."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_metadata", str(exc)) from exc

    @mcp.tool()
    def clip_set_metadata(clip_name: str, key: str, value: str) -> bool:
        """Set a single metadata field on a clip.

        Args:
            clip_name: Name of the clip to modify.
            key:       Metadata field name (e.g. "Description", "Comments").
            value:     Value to assign.

        Returns:
            True if the metadata was set successfully.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.SetMetadata(key, value)
            if not result:
                raise ResolveOperationFailed(
                    "clip_set_metadata",
                    f"Failed to set metadata '{key}' on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while setting clip metadata."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_set_metadata", str(exc)) from exc

    # ==============================================================
    # Properties
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_properties(clip_name: str) -> dict:
        """Return all clip properties (Clip Name, Duration, FPS, etc.).

        Args:
            clip_name: Name of the clip to inspect.

        Returns:
            Dict with property keys like "Clip Name", "Duration", "FPS",
            "Start TC", "End TC", "File Path", etc.
        """
        try:
            clip = _find_clip(clip_name)
            # GetClipProperty() with no args returns the full property dict
            props = clip.GetClipProperty()
            return props if isinstance(props, dict) else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip properties."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_properties", str(exc)) from exc

    @mcp.tool()
    def clip_set_property(clip_name: str, key: str, value: str) -> bool:
        """Set a single property on a clip.

        Args:
            clip_name: Name of the clip to modify.
            key:       Property key (e.g. "Clip Name", "Start TC").
            value:     Value to assign as a string.

        Returns:
            True if the property was set successfully.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.SetClipProperty(key, value)
            if not result:
                raise ResolveOperationFailed(
                    "clip_set_property",
                    f"Failed to set property '{key}' on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while setting clip property."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_set_property", str(exc)) from exc

    # ==============================================================
    # Color label
    # ==============================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_color(clip_name: str) -> str:
        """Return the label color assigned to a clip (e.g. "Orange", "Blue").

        Args:
            clip_name: Name of the clip.

        Returns:
            Color name string, or empty string if no color is set.
        """
        try:
            clip = _find_clip(clip_name)
            color: str = clip.GetClipColor() or ""
            return color
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip color."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_color", str(exc)) from exc

    @mcp.tool()
    def clip_set_color(clip_name: str, color: str) -> bool:
        """Set the label color on a clip.

        Args:
            clip_name: Name of the clip.
            color:     Color name (e.g. "Orange", "Blue", "Green", "Pink",
                       "Purple", "Fuchsia", "Rose", "Lavender", "Sky",
                       "Mint", "Lemon", "Sand", "Cocoa", "Cream").

        Returns:
            True if the color was applied.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.SetClipColor(color)
            if not result:
                raise ResolveOperationFailed(
                    "clip_set_color",
                    f"Failed to set color '{color}' on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while setting clip color."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_set_color", str(exc)) from exc

    @mcp.tool()
    def clip_clear_color(clip_name: str) -> bool:
        """Remove the label color from a clip, resetting it to the default.

        Args:
            clip_name: Name of the clip.

        Returns:
            True if the color was cleared.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.ClearClipColor()
            if not result:
                raise ResolveOperationFailed(
                    "clip_clear_color",
                    f"Failed to clear color on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while clearing clip color."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_clear_color", str(exc)) from exc

    # ==============================================================
    # Markers
    # ==============================================================

    @mcp.tool()
    def clip_add_marker(
        clip_name: str,
        frame_id: int,
        color: str,
        name: str = "",
        note: str = "",
        duration: int = 1,
        custom_data: str = "",
    ) -> bool:
        """Add a marker to a media-pool clip at a given frame.

        Args:
            clip_name:   Name of the clip.
            frame_id:    Frame number (relative to clip start) for the marker.
            color:       Marker color (e.g. "Blue", "Red", "Green").
            name:        Optional short label for the marker.
            note:        Optional longer note attached to the marker.
            duration:    Marker duration in frames (default 1).
            custom_data: Optional custom-data string stored with the marker.

        Returns:
            True if the marker was added.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.AddMarker(
                frame_id, color, name, note, duration, custom_data,
            )
            if not result:
                raise ResolveOperationFailed(
                    "clip_add_marker",
                    f"Failed to add marker at frame {frame_id} on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while adding clip marker."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_add_marker", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_markers(clip_name: str) -> dict:
        """Return all markers on a clip. Keys are frame IDs (as strings).

        Args:
            clip_name: Name of the clip.

        Returns:
            Dict mapping frame ID to marker info dict with keys:
            color, name, note, duration, customData.
        """
        try:
            clip = _find_clip(clip_name)
            markers = clip.GetMarkers()
            # Return as-is; Resolve returns {frameId: {color, name, ...}}
            return markers if isinstance(markers, dict) else {}
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip markers."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_markers", str(exc)) from exc

    @mcp.tool()
    def clip_delete_marker(clip_name: str, frame_id: int) -> bool:
        """Delete the marker at a specific frame on a clip.

        Args:
            clip_name: Name of the clip.
            frame_id:  Frame number of the marker to remove.

        Returns:
            True if the marker was deleted.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.DeleteMarkerAtFrame(frame_id)
            if not result:
                raise ResolveOperationFailed(
                    "clip_delete_marker",
                    f"No marker at frame {frame_id} on clip '{clip_name}', "
                    "or Resolve refused the deletion.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while deleting clip marker."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_delete_marker", str(exc)) from exc

    # ==============================================================
    # Flags
    # ==============================================================

    @mcp.tool()
    def clip_add_flag(clip_name: str, color: str) -> bool:
        """Add a flag of the given color to a clip.

        Args:
            clip_name: Name of the clip.
            color:     Flag color (e.g. "Blue", "Red", "Green").

        Returns:
            True if the flag was added.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.AddFlag(color)
            if not result:
                raise ResolveOperationFailed(
                    "clip_add_flag",
                    f"Failed to add '{color}' flag on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while adding clip flag."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_add_flag", str(exc)) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def clip_get_flags(clip_name: str) -> list[str]:
        """Return all flag colors currently set on a clip.

        Args:
            clip_name: Name of the clip.

        Returns:
            List of color name strings (e.g. ["Blue", "Red"]).
        """
        try:
            clip = _find_clip(clip_name)
            flags = clip.GetFlagList()
            return list(flags) if flags else []
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading clip flags."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_get_flags", str(exc)) from exc

    @mcp.tool()
    def clip_clear_flags(clip_name: str, color: str) -> bool:
        """Remove a specific flag color from a clip.

        Args:
            clip_name: Name of the clip.
            color:     Flag color to remove (e.g. "Blue").

        Returns:
            True if the flag was removed.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.ClearFlags(color)
            if not result:
                raise ResolveOperationFailed(
                    "clip_clear_flags",
                    f"Failed to clear '{color}' flag on clip '{clip_name}'.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while clearing clip flag."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_clear_flags", str(exc)) from exc

    # ==============================================================
    # Proxy media
    # ==============================================================

    @mcp.tool()
    def clip_link_proxy(clip_name: str, proxy_path: str) -> bool:
        """Link an external proxy media file to a clip.

        Args:
            clip_name:  Name of the clip.
            proxy_path: Absolute file-system path to the proxy media file.

        Returns:
            True if the proxy was linked successfully.
        """
        try:
            clip = _find_clip(clip_name)
            result: bool = clip.LinkProxyMedia(proxy_path)
            if not result:
                raise ResolveOperationFailed(
                    "clip_link_proxy",
                    f"Failed to link proxy '{proxy_path}' to clip '{clip_name}'. "
                    "Verify the file exists and the format is compatible.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while linking proxy media."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("clip_link_proxy", str(exc)) from exc
