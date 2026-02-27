"""Media Storage tools — browse mounted volumes and import files into the media pool.

DaVinci Resolve exposes a MediaStorage object that represents the physical storage
locations (drives, NAS mounts, SAN volumes) visible in the Media page's storage browser.
These tools let an MCP client list volumes, browse folders, and pull files into the
current project's media pool without touching the Resolve GUI.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


def register(mcp: FastMCP) -> None:
    """Register all media-storage tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # 1. List mounted storage volumes
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def storage_get_volumes() -> list[str]:
        """List all mounted media storage volumes visible to DaVinci Resolve.

        Returns the volume paths (e.g. '/' on macOS, 'C:\\' on Windows, or
        NAS mount points) that appear in the Media page's storage panel.
        """
        try:
            api = ResolveAPI.get_instance()
            storage = api.media_storage
            if storage is None:
                raise ResolveNotRunning("Media Storage is not available.")

            # GetMountedVolumeList() returns a list of path strings
            volumes = storage.GetMountedVolumeList()
            return volumes if volumes else []

        except AttributeError:
            # Stale scripting-bridge reference — Resolve was likely restarted
            raise ResolveNotRunning(
                "Lost connection to Resolve (stale reference). Please retry."
            )
        except ResolveNotRunning:
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "storage_get_volumes", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 2. List subfolders in a volume/folder path
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def storage_get_subfolders(volume_path: str) -> list[str]:
        """List subfolders inside a media storage path.

        Args:
            volume_path: Absolute path to a mounted volume or subfolder
                         (e.g. '/Volumes/Media/Projects').

        Returns a flat list of subfolder paths one level deep.
        """
        try:
            api = ResolveAPI.get_instance()
            storage = api.media_storage
            if storage is None:
                raise ResolveNotRunning("Media Storage is not available.")

            # GetSubFolderList() returns immediate child folder paths
            subfolders = storage.GetSubFolderList(volume_path)
            return subfolders if subfolders else []

        except AttributeError:
            raise ResolveNotRunning(
                "Lost connection to Resolve (stale reference). Please retry."
            )
        except ResolveNotRunning:
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "storage_get_subfolders", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 3. List files in a storage folder
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def storage_get_files(folder_path: str) -> list[str]:
        """List media files in a storage folder.

        Args:
            folder_path: Absolute path to the folder to scan
                         (e.g. '/Volumes/Media/Projects/Footage').

        Returns file paths found in the folder.  Resolve filters for
        recognised media formats automatically.
        """
        try:
            api = ResolveAPI.get_instance()
            storage = api.media_storage
            if storage is None:
                raise ResolveNotRunning("Media Storage is not available.")

            # GetFileList() returns file paths recognised as media
            files = storage.GetFileList(folder_path)
            return files if files else []

        except AttributeError:
            raise ResolveNotRunning(
                "Lost connection to Resolve (stale reference). Please retry."
            )
        except ResolveNotRunning:
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "storage_get_files", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 4. Import files from storage into the media pool
    # ------------------------------------------------------------------
    @mcp.tool()
    def storage_import_to_pool(file_paths: list[str]) -> list[str]:
        """Import files from media storage into the current project's media pool.

        Args:
            file_paths: List of absolute file paths to import
                        (e.g. ['/Volumes/Media/clip01.mov', '/Volumes/Media/clip02.mov']).

        Returns the names of clips that were successfully imported.  An empty
        list means nothing was imported (bad paths or unsupported formats).
        """
        try:
            api = ResolveAPI.get_instance()
            storage = api.media_storage
            if storage is None:
                raise ResolveNotRunning("Media Storage is not available.")

            # AddItemListToMediaPool() returns a list of MediaPoolItem objects
            # or None / empty list on failure
            items = storage.AddItemListToMediaPool(file_paths)

            if not items:
                return []

            # Extract the display name of each successfully imported clip
            return [item.GetName() for item in items]

        except AttributeError:
            raise ResolveNotRunning(
                "Lost connection to Resolve (stale reference). Please retry."
            )
        except ResolveNotRunning:
            raise
        except Exception as exc:
            raise ResolveOperationFailed(
                "storage_import_to_pool", str(exc)
            ) from exc
