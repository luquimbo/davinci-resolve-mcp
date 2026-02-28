"""Gallery tools — stills, albums, PowerGrades, and grade application.

Provides tools for managing the DaVinci Resolve Gallery: listing and
switching albums, grabbing/importing/exporting/deleting stills, applying
grades from gallery stills, and working with PowerGrade albums.

NOTE: Many Gallery API methods are only available in specific Resolve
versions (typically Resolve 18+ and Studio editions).  Every API call
is wrapped defensively so that unsupported operations return a clear
error rather than crashing the server.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_gallery() -> Any:
    """Return the Gallery object from the current project.

    Raises ResolveOperationFailed if no project is open or the Gallery
    is inaccessible.
    """
    api = ResolveAPI.get_instance()
    project = api.project
    if project is None:
        raise ResolveOperationFailed(
            "_get_gallery", "No project is currently open."
        )

    try:
        gallery = project.GetGallery()
    except AttributeError as exc:
        raise ResolveNotRunning(
            f"Lost connection to Resolve (stale reference: {exc}). Please retry."
        ) from exc

    if gallery is None:
        raise ResolveOperationFailed(
            "_get_gallery",
            "Gallery is not available. This may require DaVinci Resolve Studio.",
        )
    return gallery


def _find_album(name: str) -> Any:
    """Search the still album list for an album matching *name*.

    Returns the album object if found, raises ResolveOperationFailed otherwise.
    """
    gallery = _get_gallery()
    albums = gallery.GetGalleryStillAlbums()
    if not albums:
        raise ResolveOperationFailed(
            "_find_album", "No still albums found in the Gallery."
        )

    for album in albums:
        # Some Resolve versions expose GetLabel(), others expose GetName().
        # Try both to maximise compatibility.
        try:
            album_name = album.GetLabel()
        except AttributeError:
            album_name = None

        if album_name is None:
            try:
                album_name = album.GetName()
            except AttributeError:
                album_name = None

        if album_name == name:
            return album

    raise ResolveOperationFailed(
        "_find_album", f"Still album '{name}' not found."
    )


def _get_album_name(album: Any) -> str:
    """Extract the display name from an album object.

    Tries GetLabel() first (preferred), then GetName() as a fallback.
    Returns "Unnamed" if neither method is available.
    """
    try:
        label = album.GetLabel()
        if label:
            return label
    except AttributeError:
        pass

    try:
        name = album.GetName()
        if name:
            return name
    except AttributeError:
        pass

    return "Unnamed"


def _resolve_album(album_name: str | None) -> Any:
    """Return a specific album by name, or the current album if name is None.

    Consolidates the common pattern of "use given album or fall back to
    current" across multiple tools.
    """
    if album_name is not None:
        return _find_album(album_name)

    gallery = _get_gallery()
    album = gallery.GetCurrentStillAlbum()
    if album is None:
        raise ResolveOperationFailed(
            "_resolve_album",
            "No current still album is set. Specify an album_name explicitly.",
        )
    return album


def _find_powergrade_album(name: str) -> Any:
    """Search the PowerGrade album list for an album matching *name*.

    Returns the album object if found, raises ResolveOperationFailed otherwise.
    PowerGrade album APIs may not exist in all Resolve versions.
    """
    gallery = _get_gallery()

    try:
        albums = gallery.GetGalleryPowerGradeAlbums()
    except AttributeError as exc:
        raise ResolveOperationFailed(
            "_find_powergrade_album",
            "GetGalleryPowerGradeAlbums() is not available in this Resolve version.",
        ) from exc

    if not albums:
        raise ResolveOperationFailed(
            "_find_powergrade_album", "No PowerGrade albums found in the Gallery."
        )

    for album in albums:
        album_label = _get_album_name(album)
        if album_label == name:
            return album

    raise ResolveOperationFailed(
        "_find_powergrade_album", f"PowerGrade album '{name}' not found."
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all Gallery tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # 1. List still album names
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def gallery_get_albums() -> list[str]:
        """List the names of all still albums in the Gallery.

        Returns album names as strings.  Requires an open project.
        """
        try:
            gallery = _get_gallery()
            albums = gallery.GetGalleryStillAlbums()
            if not albums:
                return []
            return [_get_album_name(a) for a in albums]

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_get_albums", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 2. Get current album name
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def gallery_get_current_album() -> str:
        """Return the name of the currently active still album.

        Returns an empty string if no album is currently selected.
        """
        try:
            gallery = _get_gallery()
            album = gallery.GetCurrentStillAlbum()
            if album is None:
                return ""
            return _get_album_name(album)

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_get_current_album", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 3. Switch to a different album
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_set_current_album(album_name: str) -> bool:
        """Switch the active still album to the one matching *album_name*.

        Args:
            album_name: Exact name of the target still album.

        Returns True if the album was switched successfully.
        """
        try:
            gallery = _get_gallery()
            album = _find_album(album_name)
            result = gallery.SetCurrentStillAlbum(album)
            if not result:
                raise ResolveOperationFailed(
                    "gallery_set_current_album",
                    f"Resolve refused to switch to album '{album_name}'.",
                )
            return True

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_set_current_album", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 4. Create a new still album
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_create_album(name: str) -> bool:
        """Create a new still album in the Gallery.

        Args:
            name: Display name for the new album.

        Returns True if the album was created.
        This method may not be available in all Resolve versions.
        """
        try:
            gallery = _get_gallery()
            # CreateGalleryStillAlbum is not part of the standard documented API
            # in all versions — wrap defensively.
            result = gallery.CreateGalleryStillAlbum(name)
            if not result:
                raise ResolveOperationFailed(
                    "gallery_create_album",
                    f"Failed to create album '{name}'. "
                    "This API may not be supported in your Resolve version.",
                )
            return True

        except AttributeError as exc:
            raise ResolveOperationFailed(
                "gallery_create_album",
                "CreateGalleryStillAlbum() is not available in this Resolve version.",
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_create_album", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 5. Delete a still album
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"destructiveHint": True})
    def gallery_delete_album(album_name: str) -> bool:
        """Delete a still album from the Gallery.

        Args:
            album_name: Name of the album to delete.

        Returns True if the album was deleted.
        This method may not be available in all Resolve versions.
        """
        try:
            gallery = _get_gallery()
            album = _find_album(album_name)
            # DeleteGalleryStillAlbum is non-standard — wrap defensively.
            result = gallery.DeleteGalleryStillAlbum(album)
            if not result:
                raise ResolveOperationFailed(
                    "gallery_delete_album",
                    f"Failed to delete album '{album_name}'.",
                )
            return True

        except AttributeError as exc:
            raise ResolveOperationFailed(
                "gallery_delete_album",
                "DeleteGalleryStillAlbum() is not available in this Resolve version.",
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_delete_album", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 6. List stills in an album
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def gallery_get_stills(album_name: str | None = None) -> list[dict]:
        """List stills in a Gallery album.

        Args:
            album_name: Name of the album to list.  Uses the current album
                        if not specified.

        Returns a list of dicts, each with a "name" key (the still's label
        or a numeric index if no label is available) and an "index" key.
        """
        try:
            album = _resolve_album(album_name)
            stills = album.GetStills()
            if not stills:
                return []

            result = []
            for i, still in enumerate(stills):
                # GetLabel() is the preferred way to get a still's name;
                # fall back to the numeric index if unavailable.
                try:
                    label = still.GetLabel()
                except AttributeError:
                    label = None

                result.append({
                    "index": i,
                    "name": label if label else str(i),
                })
            return result

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_get_stills", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 7. Grab a still from the current viewer
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_grab_still() -> bool:
        """Grab a still from the current viewer into the current album.

        Captures a snapshot of whatever is currently displayed in the Resolve
        viewer and adds it to the current still album.  Equivalent to the
        "Grab Still" button in the Color page.

        Returns True if the grab succeeded.
        This may require being on the Color page with a valid viewer image.
        """
        try:
            api = ResolveAPI.get_instance()
            gallery = _get_gallery()

            # The GrabStill API may exist on the timeline, the gallery, or
            # the current still album depending on Resolve version.  Try
            # each approach in order of likelihood.

            # Approach 1: Timeline.GrabStill() — most common in newer versions
            timeline = api.timeline
            if timeline is not None:
                try:
                    result = timeline.GrabStill()
                    if result:
                        return True
                except AttributeError:
                    pass  # Method doesn't exist on this version's timeline

            # Approach 2: Gallery.GrabStill()
            try:
                result = gallery.GrabStill()
                if result:
                    return True
            except AttributeError:
                pass  # Method doesn't exist on this version's gallery

            # Approach 3: Current album's grab method
            album = gallery.GetCurrentStillAlbum()
            if album is not None:
                try:
                    result = album.GrabStill()
                    if result:
                        return True
                except AttributeError:
                    pass

            raise ResolveOperationFailed(
                "gallery_grab_still",
                "Could not grab still. Ensure you are on the Color page "
                "with a clip displayed in the viewer.",
            )

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_grab_still", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 8. Import stills from file paths
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_import_stills(
        file_paths: list[str], album_name: str | None = None
    ) -> bool:
        """Import still image files into a Gallery album.

        Args:
            file_paths:  List of absolute paths to still image files (e.g.
                         DPX, EXR, TIFF, PNG).
            album_name:  Target album name.  Uses the current album if not
                         specified.

        Returns True if the import succeeded.
        This method may not be available in all Resolve versions.
        """
        try:
            album = _resolve_album(album_name)

            # The import API may live on the album or on the gallery object,
            # depending on the Resolve version.

            # Approach 1: Album.ImportStills(file_paths)
            try:
                result = album.ImportStills(file_paths)
                if result:
                    return True
            except AttributeError:
                pass

            # Approach 2: Gallery.ImportStills(file_paths)
            gallery = _get_gallery()
            try:
                result = gallery.ImportStills(file_paths)
                if result:
                    return True
            except AttributeError:
                pass

            raise ResolveOperationFailed(
                "gallery_import_stills",
                "ImportStills() is not available in this Resolve version.",
            )

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_import_stills", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 9. Export stills by index
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_export_stills(
        still_indices: list[int],
        export_path: str,
        album_name: str | None = None,
    ) -> bool:
        """Export stills from a Gallery album to disk.

        Args:
            still_indices: Zero-based indices of stills to export (from
                           gallery_get_stills).
            export_path:   Absolute path to the output directory.
            album_name:    Source album name.  Uses the current album if
                           not specified.

        Returns True if the export succeeded.
        """
        try:
            album = _resolve_album(album_name)
            all_stills = album.GetStills()
            if not all_stills:
                raise ResolveOperationFailed(
                    "gallery_export_stills",
                    "No stills found in the specified album.",
                )

            # Select only the stills at the requested indices
            selected: list[Any] = []
            for idx in still_indices:
                if 0 <= idx < len(all_stills):
                    selected.append(all_stills[idx])

            if not selected:
                raise ResolveOperationFailed(
                    "gallery_export_stills",
                    f"No valid stills at indices {still_indices}. "
                    f"Album has {len(all_stills)} stills (0-{len(all_stills) - 1}).",
                )

            # ExportStills may accept (stills, folderPath, filePrefix, format)
            # or (stills, folderPath) depending on version.  Try the simpler
            # signature first, then the extended one.
            try:
                result = album.ExportStills(selected, export_path, "", "dpx")
            except TypeError:
                # Simpler two-argument version
                result = album.ExportStills(selected, export_path)

            if not result:
                raise ResolveOperationFailed(
                    "gallery_export_stills",
                    f"Resolve failed to export stills to '{export_path}'.",
                )
            return True

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_export_stills", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 10. Delete stills by index
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"destructiveHint": True})
    def gallery_delete_stills(
        still_indices: list[int], album_name: str | None = None
    ) -> bool:
        """Delete stills from a Gallery album by index.

        Args:
            still_indices: Zero-based indices of stills to delete (from
                           gallery_get_stills).
            album_name:    Target album name.  Uses the current album if
                           not specified.

        Returns True if the deletion succeeded.
        """
        try:
            album = _resolve_album(album_name)
            all_stills = album.GetStills()
            if not all_stills:
                raise ResolveOperationFailed(
                    "gallery_delete_stills",
                    "No stills found in the specified album.",
                )

            selected: list[Any] = []
            for idx in still_indices:
                if 0 <= idx < len(all_stills):
                    selected.append(all_stills[idx])

            if not selected:
                raise ResolveOperationFailed(
                    "gallery_delete_stills",
                    f"No valid stills at indices {still_indices}. "
                    f"Album has {len(all_stills)} stills (0-{len(all_stills) - 1}).",
                )

            result = album.DeleteStills(selected)
            if not result:
                raise ResolveOperationFailed(
                    "gallery_delete_stills",
                    "Resolve failed to delete the selected stills.",
                )
            return True

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_delete_stills", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 11. Apply a grade from a gallery still to timeline items
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_apply_grade_from_still(
        still_index: int,
        item_names: list[str],
        album_name: str | None = None,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Apply the color grade from a gallery still to timeline items.

        Args:
            still_index:  Zero-based index of the still in the album (from
                          gallery_get_stills).
            item_names:   Names of timeline items to apply the grade to.
            album_name:   Source album.  Uses the current album if not specified.
            track_type:   Track type to search for items: "video" or "audio"
                          (default "video").
            track_index:  1-based track index to search for items (default 1).

        Returns True if the grade was applied to at least one item.
        The ApplyGradeFromGalleryStill API may not exist in all Resolve versions.
        """
        try:
            api = ResolveAPI.get_instance()
            album = _resolve_album(album_name)

            # Get the still at the requested index
            all_stills = album.GetStills()
            if not all_stills or still_index < 0 or still_index >= len(all_stills):
                raise ResolveOperationFailed(
                    "gallery_apply_grade_from_still",
                    f"Still index {still_index} is out of range. "
                    f"Album has {len(all_stills) if all_stills else 0} stills.",
                )
            still = all_stills[still_index]

            # Get timeline items to apply the grade to
            timeline = api.timeline
            if timeline is None:
                raise ResolveOperationFailed(
                    "gallery_apply_grade_from_still",
                    "No timeline is currently open.",
                )

            # GetItemListInTrack returns items on a specific track
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items:
                raise ResolveOperationFailed(
                    "gallery_apply_grade_from_still",
                    f"No items found on {track_type} track {track_index}.",
                )

            # Filter items by name and apply grade to each
            target_names = set(item_names)
            applied_count = 0

            for item in items:
                if item.GetName() in target_names:
                    try:
                        # ApplyGradeFromGalleryStill is the standard method
                        # for applying a gallery grade to a timeline item.
                        result = item.ApplyGradeFromGalleryStill(still)
                        if result:
                            applied_count += 1
                    except AttributeError:
                        # Method may not exist — skip silently and report below
                        pass

            if applied_count == 0:
                raise ResolveOperationFailed(
                    "gallery_apply_grade_from_still",
                    "Grade could not be applied to any item. "
                    "ApplyGradeFromGalleryStill() may not be supported in this "
                    "Resolve version, or no items matched the given names.",
                )

            return True

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_apply_grade_from_still", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 12. List PowerGrade album names
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def gallery_get_powergrade_albums() -> list[str]:
        """List the names of all PowerGrade albums in the Gallery.

        PowerGrade albums contain grades that persist across projects.
        This method may not be available in all Resolve versions.
        """
        try:
            gallery = _get_gallery()
            albums = gallery.GetGalleryPowerGradeAlbums()
            if not albums:
                return []
            return [_get_album_name(a) for a in albums]

        except AttributeError as exc:
            raise ResolveOperationFailed(
                "gallery_get_powergrade_albums",
                "GetGalleryPowerGradeAlbums() is not available in this Resolve version.",
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_get_powergrade_albums", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 13. List stills in a PowerGrade album
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def gallery_get_powergrade_stills(album_name: str) -> list[dict]:
        """List stills in a PowerGrade album.

        Args:
            album_name: Name of the PowerGrade album.

        Returns a list of dicts with "index" and "name" keys, similar
        to gallery_get_stills.
        """
        try:
            album = _find_powergrade_album(album_name)
            stills = album.GetStills()
            if not stills:
                return []

            result = []
            for i, still in enumerate(stills):
                try:
                    label = still.GetLabel()
                except AttributeError:
                    label = None
                result.append({
                    "index": i,
                    "name": label if label else str(i),
                })
            return result

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_get_powergrade_stills", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 14. Set current PowerGrade album
    # ------------------------------------------------------------------
    @mcp.tool()
    def gallery_set_current_powergrade_album(album_name: str) -> bool:
        """Switch the active PowerGrade album to the one matching *album_name*.

        Args:
            album_name: Exact name of the target PowerGrade album.

        Returns True if the album was switched successfully.
        This method may not be available in all Resolve versions.
        """
        try:
            gallery = _get_gallery()
            album = _find_powergrade_album(album_name)

            # SetCurrentPowerGradeAlbum is non-standard — wrap defensively.
            result = gallery.SetCurrentPowerGradeAlbum(album)
            if not result:
                raise ResolveOperationFailed(
                    "gallery_set_current_powergrade_album",
                    f"Resolve refused to switch to PowerGrade album '{album_name}'.",
                )
            return True

        except AttributeError as exc:
            raise ResolveOperationFailed(
                "gallery_set_current_powergrade_album",
                "SetCurrentPowerGradeAlbum() is not available in this Resolve version.",
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "gallery_set_current_powergrade_album", str(exc)
            ) from exc
