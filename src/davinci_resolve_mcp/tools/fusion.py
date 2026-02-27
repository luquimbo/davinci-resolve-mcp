"""Fusion composition tools — comp management, generators, titles, and tool listing.

Provides access to the Fusion page features of DaVinci Resolve through the
scripting API.  Tools cover per-clip Fusion composition CRUD (add, import,
export, rename, delete), querying composition metadata and tool lists, and
inserting Fusion generators and titles into the timeline.

Timeline items are located by name using a shared helper that searches
the specified track.  Compositions are identified by name strings.  All
mutating calls return a boolean success flag; read-only tools are annotated
so MCP clients can cache or batch them.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_timeline() -> Any:
    """Return the current timeline or raise if none is open.

    Centralises the repeated "get API -> get timeline -> None check"
    boilerplate so each tool doesn't have to duplicate it.
    """
    api = ResolveAPI.get_instance()
    timeline = api.timeline
    if timeline is None:
        raise ResolveOperationFailed(
            "_require_timeline",
            "No timeline is currently open.",
        )
    return timeline


def _find_item(
    name: str,
    track_type: str = "video",
    track_index: int = 1,
) -> Any:
    """Locate a timeline item by name on the given track.

    Args:
        name:        Exact clip name to search for.
        track_type:  Track type — "video" or "audio".
        track_index: 1-based track number within the track type.

    Returns:
        The first TimelineItem whose GetName() matches *name*.

    Raises:
        ResolveOperationFailed: If the item cannot be found.
    """
    timeline = _require_timeline()

    # GetItemListInTrack() returns a list of TimelineItem objects or None
    items = timeline.GetItemListInTrack(track_type, track_index)
    if items:
        for item in items:
            if item.GetName() == name:
                return item

    raise ResolveOperationFailed(
        "_find_item",
        f"Item '{name}' not found on {track_type} track {track_index}.",
    )


def _require_media_pool() -> Any:
    """Return the MediaPool object or raise if unavailable.

    Used by generator/title insertion tools that operate on the pool
    rather than on individual timeline items.
    """
    api = ResolveAPI.get_instance()
    pool = api.media_pool
    if pool is None:
        raise ResolveOperationFailed(
            "_require_media_pool",
            "Media Pool is not available. Is a project open?",
        )
    return pool


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all Fusion composition tools on the given MCP server instance."""

    # ==================================================================
    # Composition queries
    # ==================================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def fusion_get_comp_count(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> int:
        """Return the number of Fusion compositions on a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            track_type:  Track type — "video" or "audio" (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            The composition count as an integer.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # GetFusionCompCount() returns the number of attached compositions
            count: int = item.GetFusionCompCount()
            return count
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading Fusion comp count."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_get_comp_count", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def fusion_get_comp_names(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> list[str]:
        """List the names of all Fusion compositions on a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            A list of composition name strings.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # GetFusionCompNameList() returns a list of name strings or None
            names: list[str] = item.GetFusionCompNameList() or []
            return names
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while listing Fusion comp names."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_get_comp_names", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def fusion_get_comp(
        item_name: str,
        comp_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict | None:
        """Return basic information about a Fusion composition by name.

        Args:
            item_name:   Exact name of the timeline clip.
            comp_name:   Name of the Fusion composition to query.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            A dict with "name" and "tool_count" keys if the comp exists,
            or None if not found.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # GetFusionCompByName() returns a Fusion comp object or None
            comp = item.GetFusionCompByName(comp_name)
            if comp is None:
                return None

            # Extract basic metadata from the comp object
            info: dict = {"name": comp_name}
            try:
                # GetToolList() returns a dict/list of Fusion tools in the comp
                tools = comp.GetToolList()
                info["tool_count"] = len(tools) if tools else 0
            except Exception:
                # GetToolList() might not be available; report what we can
                info["tool_count"] = -1
            return info
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while reading Fusion comp info."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_get_comp", str(exc)
            ) from exc

    # ==================================================================
    # Composition CRUD
    # ==================================================================

    @mcp.tool()
    def fusion_add_comp() -> bool:
        """Add a new Fusion composition to the timeline item under the playhead.

        This operates on the currently selected video item (the clip at the
        playhead position).  Use playback tools to position the playhead first.

        Returns:
            True if a new composition was added.
        """
        try:
            api = ResolveAPI.get_instance()
            timeline = api.timeline
            if timeline is None:
                raise ResolveOperationFailed(
                    "fusion_add_comp", "No timeline is currently open."
                )

            # Get the video item under the playhead
            current_item = timeline.GetCurrentVideoItem()
            if current_item is None:
                raise ResolveOperationFailed(
                    "fusion_add_comp",
                    "No video item under the playhead. "
                    "Move the playhead over a clip first.",
                )

            # AddFusionComp() creates a new composition on the item
            result: bool = current_item.AddFusionComp()
            if not result:
                raise ResolveOperationFailed(
                    "fusion_add_comp",
                    "Resolve refused to add a Fusion composition.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while adding Fusion comp."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_add_comp", str(exc)
            ) from exc

    @mcp.tool()
    def fusion_import_comp(
        item_name: str,
        comp_path: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Import a Fusion composition file (.comp) onto a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            comp_path:   Absolute path to the .comp file to import.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the composition was imported successfully.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # ImportFusionComp(filePath) loads a .comp file onto the item
            result: bool = item.ImportFusionComp(comp_path)
            if not result:
                raise ResolveOperationFailed(
                    "fusion_import_comp",
                    f"Failed to import Fusion comp from '{comp_path}'. "
                    "Check the file path and format (.comp).",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while importing Fusion comp."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_import_comp", str(exc)
            ) from exc

    @mcp.tool()
    def fusion_export_comp(
        item_name: str,
        comp_name: str,
        export_path: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Export a Fusion composition to a .comp file on disk.

        Args:
            item_name:   Exact name of the timeline clip.
            comp_name:   Name of the Fusion composition to export.
            export_path: Absolute destination path (should end in .comp).
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the composition was exported successfully.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # ExportFusionComp(compName, filePath) writes the comp to disk
            result: bool = item.ExportFusionComp(comp_name, export_path)
            if not result:
                raise ResolveOperationFailed(
                    "fusion_export_comp",
                    f"Failed to export Fusion comp '{comp_name}' to '{export_path}'. "
                    "Check the comp name and write permissions.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while exporting Fusion comp."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_export_comp", str(exc)
            ) from exc

    @mcp.tool()
    def fusion_delete_comp(
        item_name: str,
        comp_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Delete a Fusion composition from a timeline item by name.

        Args:
            item_name:   Exact name of the timeline clip.
            comp_name:   Name of the Fusion composition to delete.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the composition was deleted.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # DeleteFusionCompByName(compName) removes the named composition
            result: bool = item.DeleteFusionCompByName(comp_name)
            if not result:
                raise ResolveOperationFailed(
                    "fusion_delete_comp",
                    f"Failed to delete Fusion comp '{comp_name}'. "
                    "Check the name matches an existing composition.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while deleting Fusion comp."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_delete_comp", str(exc)
            ) from exc

    @mcp.tool()
    def fusion_rename_comp(
        item_name: str,
        old_name: str,
        new_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Rename a Fusion composition on a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            old_name:    Current name of the Fusion composition.
            new_name:    Desired new name.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the composition was renamed.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            # RenameFusionCompByName(oldName, newName) renames in-place
            result: bool = item.RenameFusionCompByName(old_name, new_name)
            if not result:
                raise ResolveOperationFailed(
                    "fusion_rename_comp",
                    f"Failed to rename Fusion comp '{old_name}' to '{new_name}'. "
                    "Check that the old name exists and new name is unique.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while renaming Fusion comp."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_rename_comp", str(exc)
            ) from exc

    # ==================================================================
    # Insert generators and titles
    # ==================================================================

    @mcp.tool()
    def fusion_insert_generator(generator_name: str) -> bool:
        """Insert a Fusion generator into the current timeline.

        The generator is appended at the end of the timeline via the
        Media Pool's AppendToTimeline API with mediaType "generator".

        Args:
            generator_name: Name of the Fusion generator to insert,
                            e.g. "Fusion Composition", "Text+".

        Returns:
            True if the generator was inserted successfully.
        """
        try:
            pool = _require_media_pool()
            # AppendToTimeline() accepts a list of dicts describing media to add.
            # For generators, use mediaType "generator" and generatorType for the name.
            result = pool.AppendToTimeline(
                [{"mediaType": "generator", "generatorType": generator_name}]
            )
            if not result:
                raise ResolveOperationFailed(
                    "fusion_insert_generator",
                    f"Failed to insert generator '{generator_name}'. "
                    "Check the generator name matches an available Fusion generator.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while inserting Fusion generator."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_insert_generator", str(exc)
            ) from exc

    @mcp.tool()
    def fusion_insert_title(title_name: str) -> bool:
        """Insert a Fusion title into the current timeline.

        The title is appended at the end of the timeline via the
        Media Pool's AppendToTimeline API with mediaType "title".

        Args:
            title_name: Name of the Fusion title template to insert,
                        e.g. "Text+", "Scroll".

        Returns:
            True if the title was inserted successfully.
        """
        try:
            pool = _require_media_pool()
            # Same pattern as generators, but with mediaType "title"
            result = pool.AppendToTimeline(
                [{"mediaType": "title", "generatorType": title_name}]
            )
            if not result:
                raise ResolveOperationFailed(
                    "fusion_insert_title",
                    f"Failed to insert title '{title_name}'. "
                    "Check the title name matches an available Fusion title.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while inserting Fusion title."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_insert_title", str(exc)
            ) from exc

    # ==================================================================
    # Tool listing within a composition
    # ==================================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def fusion_get_tool_list(
        item_name: str,
        comp_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> list[str]:
        """List all Fusion tools inside a specific composition.

        Args:
            item_name:   Exact name of the timeline clip.
            comp_name:   Name of the Fusion composition to inspect.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            A list of tool name strings (e.g. ["MediaIn1", "Transform1",
            "MediaOut1"]).  Returns an empty list if the comp has no tools
            or the API does not support tool listing.
        """
        try:
            item = _find_item(item_name, track_type, track_index)
            comp = item.GetFusionCompByName(comp_name)
            if comp is None:
                raise ResolveOperationFailed(
                    "fusion_get_tool_list",
                    f"Fusion composition '{comp_name}' not found on item '{item_name}'.",
                )

            # GetToolList() returns a dict-like object mapping IDs to tool objects,
            # or a list depending on the Resolve version.  We extract names safely.
            tools = comp.GetToolList()
            if not tools:
                return []

            tool_names: list[str] = []
            if isinstance(tools, dict):
                # Dict maps internal IDs to tool objects; extract the name of each
                for tool_obj in tools.values():
                    try:
                        tool_names.append(tool_obj.GetAttrs("TOOLS_Name") or str(tool_obj))
                    except Exception:
                        tool_names.append(str(tool_obj))
            elif isinstance(tools, (list, tuple)):
                for tool_obj in tools:
                    try:
                        tool_names.append(tool_obj.GetAttrs("TOOLS_Name") or str(tool_obj))
                    except Exception:
                        tool_names.append(str(tool_obj))
            else:
                # Unexpected type; return a best-effort representation
                tool_names.append(str(tools))

            return tool_names
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                "Lost connection to Resolve while listing Fusion tools."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fusion_get_tool_list", str(exc)
            ) from exc
