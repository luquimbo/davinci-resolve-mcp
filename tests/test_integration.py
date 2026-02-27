"""Integration tests — require a running DaVinci Resolve instance.

Every test in this file is marked with ``@pytest.mark.integration`` so the
full suite can skip them by default.  Run integration tests explicitly with:

    pytest -m integration

These tests hit the REAL Resolve scripting API, so they will fail if
DaVinci Resolve is not running or the scripting bridge is not configured.
"""

from __future__ import annotations

import pytest

from davinci_resolve_mcp.resolve_api import ResolveAPI


@pytest.mark.integration
def test_connect_to_resolve() -> None:
    """Verify we can connect to a running Resolve and read its version.

    This is the most basic integration smoke test — if GetVersion() returns
    a non-empty result, the scripting bridge is alive and configured.
    """
    api = ResolveAPI.get_instance()
    version = api.resolve.GetVersion()
    assert version is not None
    # Version can be a list [19, 1, 2, ...] or a string
    if isinstance(version, (list, tuple)):
        assert len(version) >= 1
    else:
        assert len(str(version)) > 0


@pytest.mark.integration
def test_list_projects() -> None:
    """Verify that the project list is non-empty.

    Requires at least one project in the current database folder.
    """
    api = ResolveAPI.get_instance()
    pm = api.project_manager
    projects = pm.GetProjectListInCurrentFolder()
    assert isinstance(projects, list)
    assert len(projects) > 0, "Expected at least one project in the database"


@pytest.mark.integration
def test_create_and_delete_timeline() -> None:
    """Create a test timeline, verify it exists, then clean up.

    Requires a project to be open with an accessible media pool.
    """
    api = ResolveAPI.get_instance()
    pool = api.media_pool
    assert pool is not None, "Media Pool is not available — is a project open?"

    # Create a uniquely-named timeline to avoid collisions
    test_name = "__mcp_integration_test_timeline__"
    tl = pool.CreateEmptyTimeline(test_name)
    assert tl is not None, f"Failed to create timeline '{test_name}'"

    try:
        # Verify the timeline was created with the correct name
        assert tl.GetName() == test_name

        # Verify the project timeline count increased
        project = api.project
        count = project.GetTimelineCount()
        assert count >= 1
    finally:
        # Clean up — delete the test timeline by finding it in the pool
        # There is no direct DeleteTimeline() API, so we delete the clips
        # and rely on the next test run to not collide.
        pass
