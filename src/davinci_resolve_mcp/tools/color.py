"""Color grading tools — node graph, LUTs, CDL, grade versions, and groups.

Provides control over DaVinci Resolve's Color page features through the
scripting API.  Tools cover per-clip node inspection, LUT assignment and
export, CDL (ASC Color Decision List) values, grade version management
(local and remote), and color group operations at the project level.

Timeline items are located by name using a shared helper that searches
the specified track.  All mutating calls return a boolean success flag;
read-only tools are annotated accordingly so MCP clients can optimise
their usage.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..models import CDLValues
from ..resolve_api import ResolveAPI
from ._helpers import find_item, require_timeline


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all color grading tools on the given MCP server instance."""

    # ==================================================================
    # Node information
    # ==================================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_num_nodes(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> int:
        """Return the number of color correction nodes on a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            track_type:  Track type — "video" or "audio" (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            The node count as an integer.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # GetNumNodes() returns the total number of corrector nodes
            count: int = item.GetNumNodes()
            return count
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_num_nodes", str(exc)
            ) from exc

    # ==================================================================
    # LUT operations
    # ==================================================================

    @mcp.tool()
    def color_set_lut(
        item_name: str,
        node_index: int,
        lut_path: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Apply a LUT file to a specific node on a timeline item.

        Args:
            item_name:   Exact name of the timeline clip.
            node_index:  1-based index of the target node.
            lut_path:    Absolute file path to the .cube / .3dl LUT file.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the LUT was applied successfully.
        """
        if node_index < 1:
            raise ResolveOperationFailed(
                "color_set_lut",
                "node_index must be >= 1 (1-based indexing).",
            )
        try:
            item = find_item(item_name, track_type, track_index)
            # SetLUT(nodeIndex, lutPath) returns True on success
            result: bool = item.SetLUT(node_index, lut_path)
            if not result:
                raise ResolveOperationFailed(
                    "color_set_lut",
                    f"Resolve refused to set LUT on node {node_index}. "
                    f"Check that the node index is valid and the path exists: {lut_path}",
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
                "color_set_lut", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_lut(
        item_name: str,
        node_index: int,
        track_type: str = "video",
        track_index: int = 1,
    ) -> str:
        """Return the LUT file path applied to a specific node, or empty string.

        Args:
            item_name:   Exact name of the timeline clip.
            node_index:  1-based index of the node to query.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            The absolute path to the applied LUT, or "" if none is set.
        """
        if node_index < 1:
            raise ResolveOperationFailed(
                "color_get_lut",
                "node_index must be >= 1 (1-based indexing).",
            )
        try:
            item = find_item(item_name, track_type, track_index)
            # GetLUT(nodeIndex) returns the LUT path string or ""
            lut_path: str = item.GetLUT(node_index) or ""
            return lut_path
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_lut", str(exc)
            ) from exc

    @mcp.tool()
    def color_export_lut(
        item_name: str,
        lut_type: str,
        export_path: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Export the combined grade of a timeline item as a LUT file.

        Args:
            item_name:   Exact name of the timeline clip.
            lut_type:    LUT format string, e.g. "3D LUT (33 Point)", "3D LUT (65 Point)".
            export_path: Absolute destination file path for the exported LUT.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the LUT was exported successfully.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # ExportLUT(exportType, filePath) writes the grade as a LUT file
            result: bool = item.ExportLUT(lut_type, export_path)
            if not result:
                raise ResolveOperationFailed(
                    "color_export_lut",
                    f"Failed to export LUT of type '{lut_type}' to '{export_path}'. "
                    "Check the format string and write permissions.",
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
                "color_export_lut", str(exc)
            ) from exc

    # ==================================================================
    # CDL (ASC Color Decision List)
    # ==================================================================

    @mcp.tool()
    def color_set_cdl(
        item_name: str,
        cdl: dict,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set ASC CDL values on a timeline item's current node.

        Args:
            item_name:   Exact name of the timeline clip.
            cdl:         CDL dictionary with keys:
                         - "Slope": [R, G, B] floats (default [1,1,1])
                         - "Offset": [R, G, B] floats (default [0,0,0])
                         - "Power": [R, G, B] floats (default [1,1,1])
                         - "Saturation": float (default 1.0)
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the CDL values were applied successfully.
        """
        try:
            item = find_item(item_name, track_type, track_index)

            # Validate CDL structure before sending to Resolve
            try:
                validated = CDLValues(
                    slope=cdl.get("Slope", [1.0, 1.0, 1.0]),
                    offset=cdl.get("Offset", [0.0, 0.0, 0.0]),
                    power=cdl.get("Power", [1.0, 1.0, 1.0]),
                    saturation=cdl.get("Saturation", 1.0),
                )
            except Exception as ve:
                raise ResolveOperationFailed(
                    "color_set_cdl",
                    f"Invalid CDL values: {ve}. Expected format: "
                    '{"Slope": [R,G,B], "Offset": [R,G,B], "Power": [R,G,B], "Saturation": float}.',
                ) from ve

            # Build the CDL dict using validated values
            cdl_dict = {
                "Slope": validated.slope,
                "Offset": validated.offset,
                "Power": validated.power,
                "Saturation": validated.saturation,
            }
            result: bool = item.SetCDL(cdl_dict)
            if not result:
                raise ResolveOperationFailed(
                    "color_set_cdl",
                    "Resolve refused the CDL values. Verify the dict format: "
                    '{"Slope": [R,G,B], "Offset": [R,G,B], "Power": [R,G,B], "Saturation": float}.',
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
                "color_set_cdl", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_cdl(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> dict:
        """Read the ASC CDL values from a timeline item's current node.

        Args:
            item_name:   Exact name of the timeline clip.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            A dict with keys: Slope ([R,G,B]), Offset ([R,G,B]),
            Power ([R,G,B]), Saturation (float).
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # GetCDL() returns a dict with Slope, Offset, Power, Saturation
            cdl: dict = item.GetCDL()
            return cdl
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_cdl", str(exc)
            ) from exc

    # ==================================================================
    # Node enable/disable
    # ==================================================================

    @mcp.tool()
    def color_set_node_enabled(
        item_name: str,
        node_index: int,
        enabled: bool,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Enable or disable a specific color correction node.

        Args:
            item_name:   Exact name of the timeline clip.
            node_index:  1-based index of the node to toggle.
            enabled:     True to enable, False to disable.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the operation succeeded.  Returns False if the Resolve
            scripting API does not support per-node enable/disable in the
            current version.
        """
        if node_index < 1:
            raise ResolveOperationFailed(
                "color_set_node_enabled",
                "node_index must be >= 1 (1-based indexing).",
            )
        try:
            item = find_item(item_name, track_type, track_index)
            # SetNodeEnabled() may not be available in all Resolve versions;
            # we attempt the call and gracefully return False if unsupported
            result: bool = item.SetNodeEnabled(node_index, enabled)
            return bool(result)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # The API method doesn't exist in this Resolve version
            return False
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_set_node_enabled", str(exc)
            ) from exc

    # ==================================================================
    # Grade application from DRX
    # ==================================================================

    @mcp.tool()
    def color_apply_drx(
        drx_path: str,
        grade_mode: int,
        item_names: list[str],
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Apply a DaVinci Resolve grade preset (.drx) to one or more items.

        Args:
            drx_path:    Absolute file path to the .drx grade file.
            grade_mode:  Grade mode: 0 = No keyframes, 1 = Source, 2 = Timeline.
            item_names:  List of timeline clip names to receive the grade.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the grade was applied to all items successfully.
        """
        try:
            # Validate grade_mode before hitting the API
            if grade_mode not in (0, 1, 2):
                raise ResolveOperationFailed(
                    "color_apply_drx",
                    f"Invalid grade_mode {grade_mode}. Must be 0 (No keyframes), "
                    "1 (Source), or 2 (Timeline).",
                )

            timeline = require_timeline()

            # Collect the TimelineItem objects for every requested name
            items: list[Any] = []
            for name in item_names:
                items.append(find_item(name, track_type, track_index))

            # ApplyGradeFromDRX(drxPath, gradeMode, item1, item2, ...)
            result: bool = timeline.ApplyGradeFromDRX(
                drx_path, grade_mode, *items
            )
            if not result:
                raise ResolveOperationFailed(
                    "color_apply_drx",
                    f"Resolve refused to apply grade from '{drx_path}'. "
                    "Check the file path and grade mode (0/1/2).",
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
                "color_apply_drx", str(exc)
            ) from exc

    # ==================================================================
    # Grade reset (identity CDL)
    # ==================================================================

    @mcp.tool(annotations={"destructiveHint": True})
    def color_reset_grade(
        item_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Reset a timeline item's grade to identity (neutral) CDL values.

        Sets Slope=[1,1,1], Offset=[0,0,0], Power=[1,1,1], Saturation=1.0.
        This effectively neutralises the grade without removing nodes.

        Args:
            item_name:   Exact name of the timeline clip.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the reset succeeded.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # Apply identity CDL values to neutralise the current grade
            identity_cdl = {
                "Slope": [1.0, 1.0, 1.0],
                "Offset": [0.0, 0.0, 0.0],
                "Power": [1.0, 1.0, 1.0],
                "Saturation": 1.0,
            }
            result: bool = item.SetCDL(identity_cdl)
            if not result:
                raise ResolveOperationFailed(
                    "color_reset_grade",
                    "Resolve refused to reset the grade to identity CDL values.",
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
                "color_reset_grade", str(exc)
            ) from exc

    # ==================================================================
    # Grade versions (local=0, remote=1)
    # ==================================================================

    @mcp.tool()
    def color_add_version(
        item_name: str,
        version_name: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Create a new local grade version on a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            version_name: Name for the new grade version.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            True if the version was created.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # AddVersion(versionName, versionType) — 0 = local, 1 = remote
            result: bool = item.AddVersion(version_name, 0)
            if not result:
                raise ResolveOperationFailed(
                    "color_add_version",
                    f"Failed to add version '{version_name}'. "
                    "The name may already exist.",
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
                "color_add_version", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_version_count(
        item_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> int:
        """Return the number of grade versions on a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            version_type: 0 for local versions, 1 for remote versions.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            The version count as an integer.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # GetVersionNameList(versionType) returns a list of name strings
            versions: list[str] = item.GetVersionNameList(version_type) or []
            return len(versions)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_version_count", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_versions(
        item_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> list[str]:
        """List all grade version names on a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            version_type: 0 for local versions (default), 1 for remote versions.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            A list of version name strings.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            versions: list[str] = item.GetVersionNameList(version_type) or []
            return versions
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_versions", str(exc)
            ) from exc

    @mcp.tool()
    def color_set_current_version(
        item_name: str,
        version_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Switch to a specific grade version on a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            version_name: Name of the version to activate.
            version_type: 0 for local (default), 1 for remote.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            True if the version was activated.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # SetCurrentVersion(versionName, versionType) switches the active version
            result: bool = item.SetCurrentVersion(version_name, version_type)
            if not result:
                raise ResolveOperationFailed(
                    "color_set_current_version",
                    f"Could not switch to version '{version_name}'. "
                    "Check the name and version type (0=local, 1=remote).",
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
                "color_set_current_version", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_current_version(
        item_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> str:
        """Return the name of the currently active grade version.

        Args:
            item_name:    Exact name of the timeline clip.
            version_type: 0 for local (default), 1 for remote.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            The active version name, or "" if unavailable.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # GetCurrentVersion(versionType) returns a dict with "versionName" key
            version_info = item.GetCurrentVersion(version_type)
            if isinstance(version_info, dict):
                return version_info.get("versionName", "")
            # Some Resolve versions return the name string directly
            return str(version_info) if version_info else ""
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_current_version", str(exc)
            ) from exc

    @mcp.tool(annotations={"destructiveHint": True})
    def color_delete_version(
        item_name: str,
        version_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Delete a grade version from a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            version_name: Name of the version to delete.
            version_type: 0 for local (default), 1 for remote.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            True if the version was deleted.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # DeleteVersion(versionName, versionType) removes a grade version
            result: bool = item.DeleteVersion(version_name, version_type)
            if not result:
                raise ResolveOperationFailed(
                    "color_delete_version",
                    f"Could not delete version '{version_name}'. "
                    "It may not exist or may be the only remaining version.",
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
                "color_delete_version", str(exc)
            ) from exc

    @mcp.tool()
    def color_rename_version(
        item_name: str,
        old_name: str,
        new_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Rename a grade version on a timeline item.

        Args:
            item_name:    Exact name of the timeline clip.
            old_name:     Current name of the version.
            new_name:     Desired new name for the version.
            version_type: 0 for local (default), 1 for remote.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            True if the version was renamed.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # RenameVersion(oldName, newName, versionType) renames in-place
            result: bool = item.RenameVersion(old_name, new_name, version_type)
            if not result:
                raise ResolveOperationFailed(
                    "color_rename_version",
                    f"Could not rename version '{old_name}' to '{new_name}'. "
                    "Check that the old name exists and the new name is unique.",
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
                "color_rename_version", str(exc)
            ) from exc

    @mcp.tool()
    def color_load_version(
        item_name: str,
        version_name: str,
        version_type: int = 0,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Load a specific grade version onto a timeline item, replacing current.

        Unlike set_current_version (which switches), load_version replaces
        the current grade data with the contents of the named version.

        Args:
            item_name:    Exact name of the timeline clip.
            version_name: Name of the version to load.
            version_type: 0 for local (default), 1 for remote.
            track_type:   Track type (default "video").
            track_index:  1-based track number (default 1).

        Returns:
            True if the version was loaded.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # LoadVersion(versionName, versionType) overwrites current grade
            result: bool = item.LoadVersion(version_name, version_type)
            if not result:
                raise ResolveOperationFailed(
                    "color_load_version",
                    f"Could not load version '{version_name}'. "
                    "Check the version name and type (0=local, 1=remote).",
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
                "color_load_version", str(exc)
            ) from exc

    # ==================================================================
    # Color groups (project-level)
    # ==================================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_group_list() -> list[dict]:
        """List all color groups defined in the current project.

        Returns:
            A list of dicts, each with at least "name" and "id" keys.
            Returns an empty list if the API is not supported or no
            groups are defined.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "color_get_group_list", "No project is currently open."
                )
            # GetColorGroupsList() returns a list of group info dicts
            groups = project.GetColorGroupsList()
            if groups is None:
                return []
            # Normalize: ensure each entry is a dict with at least name/id
            result: list[dict] = []
            for group in groups:
                if isinstance(group, dict):
                    result.append(group)
                else:
                    # Some API versions return simple strings or objects
                    result.append({"name": str(group), "id": str(group)})
            return result
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # GetColorGroupsList() may not exist in older Resolve versions
            return []
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_group_list", str(exc)
            ) from exc

    @mcp.tool()
    def color_create_group(group_name: str) -> bool:
        """Create a new color group in the current project.

        Args:
            group_name: Name for the new color group.

        Returns:
            True if the group was created.  Returns False if the API
            is not supported in the current Resolve version.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "color_create_group", "No project is currently open."
                )
            # AddColorGroup(groupName) creates a new project-level color group
            result: bool = project.AddColorGroup(group_name)
            if not result:
                raise ResolveOperationFailed(
                    "color_create_group",
                    f"Failed to create color group '{group_name}'. "
                    "The name may already exist.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # AddColorGroup() may not exist in older Resolve versions
            return False
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_create_group", str(exc)
            ) from exc

    @mcp.tool(annotations={"destructiveHint": True})
    def color_delete_group(group_id: str) -> bool:
        """Delete a color group from the current project by its ID.

        Args:
            group_id: The unique identifier of the color group to delete.
                      Obtain IDs from color_get_group_list().

        Returns:
            True if the group was deleted.  Returns False if the API
            is not supported in the current Resolve version.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "color_delete_group", "No project is currently open."
                )
            # DeleteColorGroup(groupId) removes a color group by ID
            result: bool = project.DeleteColorGroup(group_id)
            if not result:
                raise ResolveOperationFailed(
                    "color_delete_group",
                    f"Failed to delete color group '{group_id}'. "
                    "Check that the ID is valid.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # DeleteColorGroup() may not exist in older Resolve versions
            return False
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_delete_group", str(exc)
            ) from exc

    @mcp.tool()
    def color_assign_to_group(
        item_name: str,
        group_id: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Assign a timeline item to a color group.

        Args:
            item_name:   Exact name of the timeline clip.
            group_id:    ID of the target color group (from color_get_group_list).
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the item was assigned.  Returns False if the API
            is not supported in the current Resolve version.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # SetGroupMembership(groupId, True) adds the item to the group
            result: bool = item.SetGroupMembership(group_id, True)
            return bool(result)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # SetGroupMembership() may not exist in older Resolve versions
            return False
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_assign_to_group", str(exc)
            ) from exc

    @mcp.tool()
    def color_remove_from_group(
        item_name: str,
        group_id: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Remove a timeline item from a color group.

        Args:
            item_name:   Exact name of the timeline clip.
            group_id:    ID of the color group to leave (from color_get_group_list).
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the item was removed.  Returns False if the API
            is not supported in the current Resolve version.
        """
        try:
            item = find_item(item_name, track_type, track_index)
            # SetGroupMembership(groupId, False) removes the item from the group
            result: bool = item.SetGroupMembership(group_id, False)
            return bool(result)
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError:
            # SetGroupMembership() may not exist in older Resolve versions
            return False
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_remove_from_group", str(exc)
            ) from exc

    # ==================================================================
    # Node labels
    # ==================================================================

    @mcp.tool(annotations={"readOnlyHint": True})
    def color_get_node_label(
        item_name: str,
        node_index: int,
        track_type: str = "video",
        track_index: int = 1,
    ) -> str:
        """Get the label of a specific color correction node.

        Args:
            item_name:   Exact name of the timeline clip.
            node_index:  1-based index of the node to query.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            The label string for the node, or "" if none is set.
        """
        if node_index < 1:
            raise ResolveOperationFailed(
                "color_get_node_label",
                "node_index must be >= 1 (1-based indexing).",
            )
        try:
            item = find_item(item_name, track_type, track_index)
            # GetNodeLabel(nodeIndex) returns the label string for the node
            label: str = item.GetNodeLabel(node_index) or ""
            return label
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "color_get_node_label", str(exc)
            ) from exc

    @mcp.tool()
    def color_set_node_label(
        item_name: str,
        node_index: int,
        label: str,
        track_type: str = "video",
        track_index: int = 1,
    ) -> bool:
        """Set the label on a specific color correction node.

        Args:
            item_name:   Exact name of the timeline clip.
            node_index:  1-based index of the node to label.
            label:       Label string to assign to the node.
            track_type:  Track type (default "video").
            track_index: 1-based track number (default 1).

        Returns:
            True if the label was set successfully.
        """
        if node_index < 1:
            raise ResolveOperationFailed(
                "color_set_node_label",
                "node_index must be >= 1 (1-based indexing).",
            )
        try:
            item = find_item(item_name, track_type, track_index)
            # SetNodeLabel(nodeIndex, label) assigns a label to the node
            result: bool = item.SetNodeLabel(node_index, label)
            if not result:
                raise ResolveOperationFailed(
                    "color_set_node_label",
                    f"Failed to set label '{label}' on node {node_index} "
                    f"of item '{item_name}'.",
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
                "color_set_node_label", str(exc)
            ) from exc
