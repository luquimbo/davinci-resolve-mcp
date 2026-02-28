"""Project management tools — CRUD, settings, folders, import/export.

Covers the full lifecycle of DaVinci Resolve projects: listing, creating,
opening, saving, closing, deleting, and configuring settings.  Also provides
folder navigation within the project database and .drp import/export.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


def register(mcp: FastMCP) -> None:
    """Register all project management tools on *mcp*."""

    # ------------------------------------------------------------------
    # Project listing / CRUD
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def project_list() -> list[str]:
        """List all project names in the current database folder.

        Returns an alphabetically-ordered list of project name strings.
        """
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # GetProjectListInCurrentFolder() returns a list of name strings
            projects: list[str] = pm.GetProjectListInCurrentFolder() or []
            return projects
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_list", str(exc)) from exc

    @mcp.tool()
    def project_create(name: str) -> str:
        """Create a new project and open it immediately.

        Args:
            name: The name for the new project.  Must be unique within
                  the current database folder.

        Returns:
            The name of the created project.
        """
        # Reject empty or whitespace-only names before hitting the API
        if not name or not name.strip():
            raise ResolveOperationFailed("project_create", "Project name cannot be empty.")
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # CreateProject() returns the new project object or None on failure
            new_project = pm.CreateProject(name)
            if new_project is None:
                raise ResolveOperationFailed(
                    "project_create",
                    f"Could not create project '{name}'. "
                    "A project with that name may already exist.",
                )
            return new_project.GetName()
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_create", str(exc)) from exc

    @mcp.tool()
    def project_open(name: str) -> bool:
        """Open an existing project by name.

        Args:
            name: Exact name of the project to open.  The current project
                  will be closed automatically (and saved first by Resolve).

        Returns:
            True if the project was opened successfully.
        """
        # Reject empty or whitespace-only names before hitting the API
        if not name or not name.strip():
            raise ResolveOperationFailed("project_open", "Project name cannot be empty.")
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # LoadProject() returns the project object or None on failure
            project = pm.LoadProject(name)
            if project is None:
                raise ResolveOperationFailed(
                    "project_open",
                    f"Could not open project '{name}'. "
                    "Check the name and ensure it exists in the current folder.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_open", str(exc)) from exc

    @mcp.tool()
    def project_save() -> bool:
        """Save the current project.

        Returns:
            True if the save succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_save", "No project is currently open."
                )
            # SaveProject() returns True on success
            result: bool = project.SaveProject()
            if not result:
                raise ResolveOperationFailed(
                    "project_save", "Resolve returned False when saving."
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_save", str(exc)) from exc

    @mcp.tool()
    def project_close() -> bool:
        """Close the current project (saves automatically before closing).

        Returns:
            True if the project was closed successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_close", "No project is currently open."
                )
            pm = api.project_manager
            # CloseProject() saves and closes; returns True on success
            result: bool = pm.CloseProject(project)
            if not result:
                raise ResolveOperationFailed(
                    "project_close",
                    "Resolve refused to close the project.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_close", str(exc)) from exc

    @mcp.tool(annotations={"destructiveHint": True})
    def project_delete(name: str) -> bool:
        """Delete a project by name.  The project must NOT be currently open.

        Args:
            name: Exact name of the project to delete.  This action is
                  irreversible.

        Returns:
            True if the project was deleted.
        """
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # DeleteProject() returns True on success, False if the project
            # is open, doesn't exist, or can't be deleted
            result: bool = pm.DeleteProject(name)
            if not result:
                raise ResolveOperationFailed(
                    "project_delete",
                    f"Could not delete project '{name}'. "
                    "Ensure it exists and is not currently open.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_delete", str(exc)) from exc

    # ------------------------------------------------------------------
    # Current project info
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def project_get_current() -> dict:
        """Return basic info about the currently open project.

        Returns:
            A dict with keys: name (str), timeline_count (int).
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_get_current", "No project is currently open."
                )
            return {
                "name": project.GetName(),
                "timeline_count": project.GetTimelineCount(),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_get_current", str(exc)) from exc

    # ------------------------------------------------------------------
    # Project settings
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def project_get_setting(key: str) -> str:
        """Read a single project setting by its key.

        Args:
            key: The setting key, e.g. "timelineFrameRate",
                 "timelineResolutionWidth".  See the Resolve Scripting API
                 docs for the full list of valid keys.

        Returns:
            The setting value as a string.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_get_setting", "No project is currently open."
                )
            # GetSetting() returns a string value or "" if key is invalid
            value: str = project.GetSetting(key)
            return value
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_get_setting", str(exc)) from exc

    @mcp.tool()
    def project_set_setting(key: str, value: str) -> bool:
        """Write a project setting.

        Args:
            key: The setting key (e.g. "timelineFrameRate").
            value: The new value as a string (e.g. "24").

        Returns:
            True if the setting was applied successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_set_setting", "No project is currently open."
                )
            # SetSetting() returns True on success
            result: bool = project.SetSetting(key, value)
            if not result:
                raise ResolveOperationFailed(
                    "project_set_setting",
                    f"Resolve rejected setting '{key}' = '{value}'. "
                    "The key may be invalid or the value out of range.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_set_setting", str(exc)) from exc

    # ------------------------------------------------------------------
    # Import / Export
    # ------------------------------------------------------------------

    @mcp.tool()
    def project_import(file_path: str) -> bool:
        """Import a .drp project file into the current database folder.

        Args:
            file_path: Absolute path to the .drp file to import.

        Returns:
            True if the import succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # ImportProject() returns True on success
            result: bool = pm.ImportProject(file_path)
            if not result:
                raise ResolveOperationFailed(
                    "project_import",
                    f"Could not import '{file_path}'. "
                    "Check the path and file format (.drp).",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_import", str(exc)) from exc

    @mcp.tool()
    def project_export(file_path: str, with_stills_and_luts: bool = True) -> bool:
        """Export the current project to a .drp file.

        Args:
            file_path: Absolute destination path (should end in .drp).
            with_stills_and_luts: If True (default), include stills and LUTs
                                  in the exported file.  Set to False for a
                                  smaller file without color assets.

        Returns:
            True if the export succeeded.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "project_export", "No project is currently open."
                )
            # ExportProject() returns True on success
            result: bool = project.ExportProject(file_path, with_stills_and_luts)
            if not result:
                raise ResolveOperationFailed(
                    "project_export",
                    f"Could not export to '{file_path}'. "
                    "Check the path and write permissions.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_export", str(exc)) from exc

    # ------------------------------------------------------------------
    # Database folder navigation
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def project_folder_list() -> list[str]:
        """List sub-folders in the current database folder.

        Returns:
            A list of folder name strings.
        """
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # GetFolderListInCurrentFolder() returns a list of folder names
            folders: list[str] = pm.GetFolderListInCurrentFolder() or []
            return folders
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_folder_list", str(exc)) from exc

    @mcp.tool()
    def project_folder_open(folder_name: str) -> bool:
        """Navigate into a sub-folder within the project database.

        Args:
            folder_name: Name of the folder to open.

        Returns:
            True if the folder was opened successfully.
        """
        try:
            api = ResolveAPI.get_instance()
            pm = api.project_manager
            # OpenFolder() returns True on success
            result: bool = pm.OpenFolder(folder_name)
            if not result:
                raise ResolveOperationFailed(
                    "project_folder_open",
                    f"Could not open folder '{folder_name}'. "
                    "Check the name and ensure it exists.",
                )
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed("project_folder_open", str(exc)) from exc
