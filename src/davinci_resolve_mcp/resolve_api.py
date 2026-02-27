"""Lazy singleton that connects to the running DaVinci Resolve instance.

Platform auto-detection adds the correct scripting modules path before importing
the Resolve scripting library.  A health-check (`GetVersion()`) runs on every
access to detect stale references and reconnect automatically.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
from typing import Any

from .exceptions import ResolveNotRunning


def _get_modules_path() -> str:
    """Return the platform-specific path to Resolve's scripting modules."""
    system = platform.system()
    if system == "Darwin":
        return (
            "/Library/Application Support/Blackmagic Design/"
            "DaVinci Resolve/Developer/Scripting/Modules/"
        )
    elif system == "Windows":
        return os.path.join(
            os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
            "Blackmagic Design",
            "DaVinci Resolve",
            "Support",
            "Developer",
            "Scripting",
            "Modules",
        )
    else:  # Linux
        return "/opt/resolve/Developer/Scripting/Modules/"


def _load_resolve_script() -> Any:
    """Import DaVinciResolveScript from the platform-specific path."""
    modules_path = _get_modules_path()

    # Ensure the path is on sys.path so `import DaVinciResolveScript` works
    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)

    # Also set the env var Resolve expects (macOS/Linux)
    os.environ.setdefault("RESOLVE_SCRIPT_API", modules_path)
    os.environ.setdefault("RESOLVE_SCRIPT_LIB", os.path.join(
        modules_path, "..", "Libraries",
    ))

    try:
        # Dynamically import — module isn't available at install time
        mod = importlib.import_module("DaVinciResolveScript")
        return mod
    except ImportError as exc:
        raise ResolveNotRunning(
            "Could not import DaVinciResolveScript. "
            f"Looked in: {modules_path}. "
            "Make sure DaVinci Resolve is installed."
        ) from exc


class ResolveAPI:
    """Lazy singleton providing access to the Resolve scripting API.

    Usage::

        api = ResolveAPI.get_instance()
        version = api.resolve.GetVersion()
        pm = api.project_manager
        project = api.project
        timeline = api.timeline
        media_pool = api.media_pool
        media_storage = api.media_storage
    """

    _instance: ResolveAPI | None = None

    def __init__(self) -> None:
        self._resolve: Any = None
        self._script_module: Any = None

    # ------------------------------------------------------------------
    # Singleton access
    # ------------------------------------------------------------------
    @classmethod
    def get_instance(cls) -> ResolveAPI:
        """Return the shared instance, creating it on first call."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Drop the singleton (useful for tests)."""
        cls._instance = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def _connect(self) -> Any:
        """Connect to the running Resolve instance via the scripting bridge."""
        if self._script_module is None:
            self._script_module = _load_resolve_script()

        resolve = self._script_module.scriptapp("Resolve")
        if resolve is None:
            raise ResolveNotRunning()
        return resolve

    def _ensure_connected(self) -> Any:
        """Return a live Resolve reference, reconnecting if stale."""
        if self._resolve is not None:
            try:
                # Quick health check — cheapest API call
                self._resolve.GetVersion()
                return self._resolve
            except Exception:
                # Stale reference — reconnect
                self._resolve = None

        self._resolve = self._connect()
        return self._resolve

    # ------------------------------------------------------------------
    # Convenience properties — each call validates the connection first
    # ------------------------------------------------------------------
    @property
    def resolve(self) -> Any:
        """The root Resolve scripting object."""
        return self._ensure_connected()

    @property
    def project_manager(self) -> Any:
        """Resolve → GetProjectManager()."""
        pm = self.resolve.GetProjectManager()
        if pm is None:
            raise ResolveNotRunning("Could not access Project Manager.")
        return pm

    @property
    def project(self) -> Any:
        """Current open project (may be None if no project is open)."""
        return self.project_manager.GetCurrentProject()

    @property
    def media_pool(self) -> Any:
        """Current project → GetMediaPool()."""
        proj = self.project
        if proj is None:
            return None
        return proj.GetMediaPool()

    @property
    def media_storage(self) -> Any:
        """Resolve → GetMediaStorage()."""
        return self.resolve.GetMediaStorage()

    @property
    def timeline(self) -> Any:
        """Current project → GetCurrentTimeline() (may be None)."""
        proj = self.project
        if proj is None:
            return None
        return proj.GetCurrentTimeline()
