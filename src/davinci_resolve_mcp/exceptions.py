"""Custom exceptions for DaVinci Resolve MCP operations."""


class ResolveNotRunning(Exception):
    """Raised when DaVinci Resolve is not running or the scripting API is unreachable."""

    def __init__(self, message: str | None = None):
        super().__init__(
            message
            or "DaVinci Resolve is not running. Please open it and try again."
        )


class ResolveOperationFailed(Exception):
    """Raised when a Resolve API call returns an error or unexpected result."""

    def __init__(self, operation: str, detail: str = ""):
        # Include the operation name so the LLM can diagnose what went wrong
        msg = f"Resolve operation failed: {operation}"
        if detail:
            msg += f" — {detail}"
        super().__init__(msg)
