"""FastMCP server — registers every tool and resource module, then runs.

Entry point: `davinci-resolve-mcp` (see pyproject.toml [project.scripts]).
"""

from fastmcp import FastMCP

# Import registration functions from each domain module
from .tools import (
    playback,
    project,
    media_storage,
    media_pool,
    media_pool_item,
    timeline,
    timeline_item,
    render,
    color,
    fusion,
    gallery,
    fairlight,
)
from .resources import system_info, project_info, timeline_info

# Create the MCP server instance — FastMCP v2 only takes the name positional arg
mcp = FastMCP("DaVinci Resolve")

# ---------------------------------------------------------------------------
# Register every tool module — each adds its @mcp.tool() functions
# ---------------------------------------------------------------------------
_TOOL_MODULES = [
    # Phase 1: Core
    playback,
    project,
    media_storage,
    media_pool,
    media_pool_item,
    timeline,
    timeline_item,
    render,
    # Phase 2: Color + Fusion
    color,
    fusion,
    # Phase 3: Gallery + Fairlight
    gallery,
    fairlight,
]

for mod in _TOOL_MODULES:
    mod.register(mcp)

# ---------------------------------------------------------------------------
# Register resources
# ---------------------------------------------------------------------------
_RESOURCE_MODULES = [
    system_info,
    project_info,
    timeline_info,
]

for mod in _RESOURCE_MODULES:
    mod.register(mcp)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Start the MCP server (stdio transport by default)."""
    mcp.run()


if __name__ == "__main__":
    main()
