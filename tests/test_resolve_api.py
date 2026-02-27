"""Tests for the ResolveAPI singleton lifecycle.

Covers: singleton identity, reset behavior, and platform-specific path detection.
These tests do NOT require a running DaVinci Resolve instance — they exercise
the singleton logic and platform-detection code paths with mocks.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from davinci_resolve_mcp.resolve_api import ResolveAPI, _get_modules_path


# ---------------------------------------------------------------------------
# Singleton behavior
# ---------------------------------------------------------------------------

class TestSingleton:
    """Verify that get_instance() returns the same object and reset() clears it."""

    def setup_method(self) -> None:
        """Ensure a clean singleton state before each test."""
        ResolveAPI.reset()

    def teardown_method(self) -> None:
        """Clean up singleton after each test."""
        ResolveAPI.reset()

    def test_singleton_same_instance(self) -> None:
        """Two consecutive get_instance() calls return the exact same object."""
        a = ResolveAPI.get_instance()
        b = ResolveAPI.get_instance()
        assert a is b

    def test_reset_clears_instance(self) -> None:
        """After reset(), the next get_instance() creates a new object."""
        first = ResolveAPI.get_instance()
        ResolveAPI.reset()
        second = ResolveAPI.get_instance()
        # They should be different objects since reset() cleared the singleton
        assert first is not second


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

class TestPlatformDetection:
    """Verify _get_modules_path() returns correct paths per platform."""

    def test_macos_path(self) -> None:
        """On macOS (Darwin), the modules path points to /Library/Application Support/."""
        with patch("davinci_resolve_mcp.resolve_api.platform.system", return_value="Darwin"):
            path = _get_modules_path()
            assert "Library/Application Support" in path
            assert "DaVinci Resolve" in path
            assert path.endswith("Modules/")

    def test_windows_path(self) -> None:
        """On Windows, the modules path points to ProgramData."""
        with patch("davinci_resolve_mcp.resolve_api.platform.system", return_value="Windows"):
            with patch.dict("os.environ", {"PROGRAMDATA": r"C:\ProgramData"}):
                path = _get_modules_path()
                assert "ProgramData" in path
                assert "Modules" in path

    def test_linux_path(self) -> None:
        """On Linux, the modules path points to /opt/resolve/."""
        with patch("davinci_resolve_mcp.resolve_api.platform.system", return_value="Linux"):
            path = _get_modules_path()
            assert path.startswith("/opt/resolve/")
            assert path.endswith("Modules/")
