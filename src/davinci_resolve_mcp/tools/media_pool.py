"""Media Pool tools — folder CRUD, clip management, timeline creation, and metadata export.

The Media Pool is the central clip library for a DaVinci Resolve project.  It organises
media into a folder tree, lets you import/move/delete clips, and serves as the source
for timeline creation.  These tools expose the full Media Pool API surface so an MCP
client can manage media without interacting with the Resolve GUI.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_pool() -> Any:
    """Return the MediaPool object or raise if unavailable.

    Centralises the "get API -> get pool -> check None" boilerplate so every
    tool doesn't have to repeat it.
    """
    api = ResolveAPI.get_instance()
    pool = api.media_pool
    if pool is None:
        raise ResolveNotRunning(
            "Media Pool is not available. Is a project open?"
        )
    return pool


def _require_current_folder() -> Any:
    """Return the current Media Pool folder or raise."""
    pool = _require_pool()
    folder = pool.GetCurrentFolder()
    if folder is None:
        raise ResolveOperationFailed(
            "_require_current_folder",
            "No current folder set in the Media Pool.",
        )
    return folder


def _find_subfolder_by_name(parent_folder: Any, name: str) -> Any | None:
    """Search immediate children of *parent_folder* for a subfolder matching *name*.

    Returns the folder object if found, otherwise None.
    """
    subfolders = parent_folder.GetSubFolderList()
    if not subfolders:
        return None
    for folder in subfolders:
        if folder.GetName() == name:
            return folder
    return None


def _find_clips_by_names(
    folder: Any, clip_names: list[str]
) -> list[Any]:
    """Return MediaPoolItem objects whose names match the given list.

    Searches the clip list of *folder*.  Only exact name matches are returned.
    Unmatched names are silently skipped (the caller decides how to handle).
    """
    clips = folder.GetClipList()
    if not clips:
        return []

    # Build a lookup set for O(n) matching instead of O(n*m)
    target_set = set(clip_names)
    return [clip for clip in clips if clip.GetName() in target_set]


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all media-pool tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # 1. Get root folder name
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def media_pool_get_root_folder() -> str:
        """Get the name of the Media Pool's root folder.

        Every project has exactly one root folder (usually named 'Master').
        """
        try:
            pool = _require_pool()
            root = pool.GetRootFolder()
            if root is None:
                raise ResolveOperationFailed(
                    "media_pool_get_root_folder", "Root folder is None."
                )
            return root.GetName()

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_get_root_folder", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 2. Get current folder name
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def media_pool_get_current_folder() -> str:
        """Get the name of the currently selected Media Pool folder."""
        try:
            folder = _require_current_folder()
            return folder.GetName()

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_get_current_folder", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 3. Navigate to a folder by name
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_set_current_folder(folder_name: str) -> bool:
        """Navigate into a Media Pool folder by name.

        Args:
            folder_name: Exact name of the target folder.

        Searches the immediate children of both the current folder and the root
        folder.  Returns True if navigation succeeded.
        """
        try:
            pool = _require_pool()

            # First, look in the current folder's children
            current = pool.GetCurrentFolder()
            if current is not None:
                target = _find_subfolder_by_name(current, folder_name)
                if target is not None:
                    return bool(pool.SetCurrentFolder(target))

            # Fall back to searching root folder's children
            root = pool.GetRootFolder()
            if root is not None:
                target = _find_subfolder_by_name(root, folder_name)
                if target is not None:
                    return bool(pool.SetCurrentFolder(target))

            raise ResolveOperationFailed(
                "media_pool_set_current_folder",
                f"Folder '{folder_name}' not found in current or root folder.",
            )

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_set_current_folder", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 4. Create a subfolder
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_create_folder(name: str) -> bool:
        """Create a new subfolder inside the current Media Pool folder.

        Args:
            name: Name for the new subfolder.

        Returns True if the folder was created.
        """
        # Validate the folder name before calling Resolve
        if not name or not name.strip():
            raise ResolveOperationFailed("media_pool_create_folder", "Folder name cannot be empty.")

        try:
            pool = _require_pool()
            current = _require_current_folder()

            result = pool.AddSubFolder(current, name)
            if result is None:
                raise ResolveOperationFailed(
                    "media_pool_create_folder",
                    f"Failed to create folder '{name}'. It may already exist.",
                )
            return True

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_create_folder", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 5. Delete folders by name
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"destructiveHint": True})
    def media_pool_delete_folders(folder_names: list[str]) -> bool:
        """Delete Media Pool subfolders by name.

        Args:
            folder_names: List of folder names to delete (searched in the
                          current folder's children).

        Returns True if the operation succeeded.  Folders that are not found
        are silently skipped.
        """
        try:
            pool = _require_pool()
            current = _require_current_folder()

            # Collect folder objects matching the requested names
            target_set = set(folder_names)
            subfolders = current.GetSubFolderList() or []
            folder_objs = [f for f in subfolders if f.GetName() in target_set]

            if not folder_objs:
                raise ResolveOperationFailed(
                    "media_pool_delete_folders",
                    "None of the specified folders were found.",
                )

            result = pool.DeleteFolders(folder_objs)
            return bool(result)

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_delete_folders", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 6. Get clips in current folder (paginated)
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def media_pool_get_clips(offset: int = 0, limit: int = 50) -> dict:
        """List clips in the current Media Pool folder with pagination.

        Args:
            offset: Number of clips to skip (default 0).
            limit:  Maximum clips to return per page (default 50).

        Returns a dict with keys: items, total, offset, limit, has_more.
        Each item contains: name, clip_color, duration, fps, resolution.
        """
        # Clamp offset and limit to sensible minimums
        offset = max(0, offset)
        limit = max(1, limit)

        try:
            folder = _require_current_folder()

            all_clips = folder.GetClipList() or []
            total = len(all_clips)

            # Slice the list for the requested page
            page = all_clips[offset : offset + limit]

            items = []
            for clip in page:
                # Extract commonly useful clip properties safely
                props = clip.GetClipProperty() if clip else {}
                if not isinstance(props, dict):
                    props = {}

                items.append(
                    {
                        "name": clip.GetName() if clip else "Unknown",
                        "clip_color": props.get("Clip Color", ""),
                        "duration": props.get("Duration", ""),
                        "fps": props.get("FPS", ""),
                        "resolution": props.get("Resolution", ""),
                    }
                )

            return {
                "items": items,
                "total": total,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + limit) < total,
            }

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_get_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 7. List subfolder names in current folder
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def media_pool_get_subfolders() -> list[str]:
        """List the names of all subfolders in the current Media Pool folder."""
        try:
            folder = _require_current_folder()
            subfolders = folder.GetSubFolderList() or []
            return [f.GetName() for f in subfolders]

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_get_subfolders", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 8. Import media files into current folder
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_import_media(file_paths: list[str]) -> list[str]:
        """Import media files from disk into the current Media Pool folder.

        Args:
            file_paths: Absolute paths to media files to import.

        Returns the names of successfully imported clips.
        """
        try:
            pool = _require_pool()

            # ImportMedia() takes a list of file path strings and returns
            # a list of MediaPoolItem objects (or None on failure)
            items = pool.ImportMedia(file_paths)

            if not items:
                return []

            return [item.GetName() for item in items]

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_import_media", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 9. Create an empty timeline
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_create_timeline(name: str) -> str:
        """Create a new empty timeline in the current Media Pool folder.

        Args:
            name: Name for the new timeline.

        Returns the name of the created timeline.
        """
        # Validate the timeline name before calling Resolve
        if not name or not name.strip():
            raise ResolveOperationFailed("media_pool_create_timeline", "Timeline name cannot be empty.")

        try:
            pool = _require_pool()
            timeline = pool.CreateEmptyTimeline(name)

            if timeline is None:
                raise ResolveOperationFailed(
                    "media_pool_create_timeline",
                    f"Failed to create timeline '{name}'.",
                )

            return timeline.GetName()

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_create_timeline", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 10. Create a timeline from clips by name
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_create_timeline_from_clips(
        name: str, clip_names: list[str]
    ) -> str:
        """Create a new timeline populated with specific clips from the current folder.

        Args:
            name:       Name for the new timeline.
            clip_names: Ordered list of clip names to include.  Clips are
                        searched in the current Media Pool folder.

        Returns the name of the created timeline.
        """
        # Validate the timeline name before calling Resolve
        if not name or not name.strip():
            raise ResolveOperationFailed("media_pool_create_timeline_from_clips", "Timeline name cannot be empty.")

        try:
            pool = _require_pool()
            folder = _require_current_folder()

            clip_objs = _find_clips_by_names(folder, clip_names)
            if not clip_objs:
                raise ResolveOperationFailed(
                    "media_pool_create_timeline_from_clips",
                    "No matching clips found in the current folder.",
                )

            timeline = pool.CreateTimelineFromClips(name, clip_objs)
            if timeline is None:
                raise ResolveOperationFailed(
                    "media_pool_create_timeline_from_clips",
                    f"Failed to create timeline '{name}' from the given clips.",
                )

            return timeline.GetName()

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_create_timeline_from_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 11. Delete clips by name
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"destructiveHint": True})
    def media_pool_delete_clips(clip_names: list[str]) -> bool:
        """Delete clips from the current Media Pool folder by name.

        Args:
            clip_names: Names of clips to delete.

        Returns True if the operation succeeded.  Clips not found are
        silently skipped.
        """
        try:
            pool = _require_pool()
            folder = _require_current_folder()

            clip_objs = _find_clips_by_names(folder, clip_names)
            if not clip_objs:
                raise ResolveOperationFailed(
                    "media_pool_delete_clips",
                    "None of the specified clips were found.",
                )

            result = pool.DeleteClips(clip_objs)
            return bool(result)

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_delete_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 12. Move clips to another folder
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_move_clips(
        clip_names: list[str], target_folder_name: str
    ) -> bool:
        """Move clips from the current folder to a different Media Pool folder.

        Args:
            clip_names:         Names of clips to move.
            target_folder_name: Name of the destination folder (searched in
                                the current folder's siblings and root children).

        Returns True if the clips were moved successfully.
        """
        try:
            pool = _require_pool()
            folder = _require_current_folder()

            # Find the clip objects to move
            clip_objs = _find_clips_by_names(folder, clip_names)
            if not clip_objs:
                raise ResolveOperationFailed(
                    "media_pool_move_clips",
                    "None of the specified clips were found.",
                )

            # Locate the target folder: check current folder's parent (root) children
            root = pool.GetRootFolder()
            target = _find_subfolder_by_name(root, target_folder_name)

            # Also check current folder's children in case target is nested here
            if target is None:
                target = _find_subfolder_by_name(folder, target_folder_name)

            if target is None:
                raise ResolveOperationFailed(
                    "media_pool_move_clips",
                    f"Target folder '{target_folder_name}' not found.",
                )

            result = pool.MoveClips(clip_objs, target)
            return bool(result)

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_move_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 13. Relink clips to new file paths
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_relink_clips(
        clip_names: list[str], new_folder_path: str
    ) -> bool:
        """Relink offline clips to media files in a new folder.

        Args:
            clip_names:      Names of clips to relink.
            new_folder_path: Absolute path to the folder containing the
                             replacement media files.  Resolve matches by
                             filename within this folder.

        Returns True if relinking succeeded.
        """
        try:
            pool = _require_pool()
            folder = _require_current_folder()

            clip_objs = _find_clips_by_names(folder, clip_names)
            if not clip_objs:
                raise ResolveOperationFailed(
                    "media_pool_relink_clips",
                    "None of the specified clips were found.",
                )

            result = pool.RelinkClips(clip_objs, new_folder_path)
            return bool(result)

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_relink_clips", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 14. Export metadata to CSV
    # ------------------------------------------------------------------
    @mcp.tool()
    def media_pool_export_metadata(file_path: str) -> bool:
        """Export metadata of all clips in the current folder to a CSV file.

        Args:
            file_path: Absolute path for the output CSV file
                       (e.g. '/Users/me/Desktop/metadata.csv').

        Returns True if the export succeeded.
        """
        try:
            pool = _require_pool()
            folder = _require_current_folder()

            clips = folder.GetClipList()
            if not clips:
                raise ResolveOperationFailed(
                    "media_pool_export_metadata",
                    "No clips in the current folder to export.",
                )

            result = pool.ExportMetadata(file_path, clips)
            if not result:
                raise ResolveOperationFailed(
                    "media_pool_export_metadata",
                    f"Resolve failed to export metadata to '{file_path}'.",
                )
            return True

        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "media_pool_export_metadata", str(exc)
            ) from exc
