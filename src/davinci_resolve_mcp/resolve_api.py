"""Lazy singleton that connects to the running DaVinci Resolve instance.

Platform auto-detection adds the correct scripting modules path before importing
the Resolve scripting library.  A health-check runs periodically to detect stale
references and reconnect automatically.
"""

from __future__ import annotations

import importlib
import os
import platform
import sys
import threading
import time
from types import ModuleType
from typing import Any

from .exceptions import ResolveNotRunning

# How many seconds to cache a successful health check before re-checking
_HEALTH_CHECK_TTL = 5.0


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


def _load_resolve_script() -> ModuleType:
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
    """Lazy, thread-safe singleton providing access to the Resolve scripting API.

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
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._resolve: Any = None
        self._script_module: ModuleType | None = None
        self._last_health_check: float = 0.0
        # Protects _resolve and _last_health_check from concurrent access.
        # Uses RLock so callers that hold the lock can safely re-enter
        # (e.g. a property that calls _ensure_connected).
        self._conn_lock = threading.RLock()

    # ------------------------------------------------------------------
    # Singleton access (thread-safe)
    # ------------------------------------------------------------------
    @classmethod
    def get_instance(cls) -> ResolveAPI:
        """Return the shared instance, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking — re-check after acquiring lock
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Drop the singleton (useful for tests)."""
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def _connect(self) -> Any:
        """Connect to the running Resolve instance via the scripting bridge."""
        if self._script_module is None:
            self._script_module = _load_resolve_script()

        resolve = self._script_module.scriptapp("Resolve")  # type: ignore[union-attr]
        if resolve is None:
            raise ResolveNotRunning()
        return resolve

    def _ensure_connected(self) -> Any:
        """Return a live Resolve reference, reconnecting if stale.

        Caches successful health checks for ``_HEALTH_CHECK_TTL`` seconds
        to avoid unnecessary IPC calls on rapid successive tool invocations.

        Thread-safe: the entire check-and-reconnect sequence is serialised
        through ``_conn_lock`` so concurrent callers cannot race on
        ``_resolve`` / ``_last_health_check``.
        """
        with self._conn_lock:
            now = time.monotonic()

            if self._resolve is not None:
                # If last check was recent enough, skip the IPC round-trip
                if (now - self._last_health_check) < _HEALTH_CHECK_TTL:
                    return self._resolve
                try:
                    # Quick health check — cheapest API call
                    self._resolve.GetVersion()
                    self._last_health_check = now
                    return self._resolve
                except Exception:
                    # Stale reference — reconnect
                    self._resolve = None

            self._resolve = self._connect()
            self._last_health_check = time.monotonic()
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
