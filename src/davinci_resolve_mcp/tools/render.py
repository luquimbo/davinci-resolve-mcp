"""Render queue tools — formats, codecs, presets, jobs, and render control.

Provides full control over the Deliver page workflow: querying available
formats and codecs, loading presets, configuring render settings, managing
the job queue (add/delete/list), and starting/stopping renders with
progress monitoring.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI

# Allowed keys for render_set_settings — keeps a clear contract so callers
# know exactly which settings are accepted without digging into Resolve docs.
_VALID_RENDER_SETTING_KEYS = {
    "TargetDir",
    "CustomName",
    "FormatWidth",
    "FormatHeight",
    "FrameRate",
    "MarkIn",
    "MarkOut",
    "AudioCodec",
    "AudioBitDepth",
    "AudioSampleRate",
    "ExportAlpha",
}


def _require_project() -> tuple:
    """Return (api, project) or raise if no project is open.

    Centralises the repeated pattern of grabbing the API singleton and
    checking that a project exists before touching render methods.
    """
    api = ResolveAPI.get_instance()
    project = api.project
    if project is None:
        raise ResolveOperationFailed(
            "render", "No project is currently open."
        )
    return api, project


def register(mcp: FastMCP) -> None:
    """Register all render / Deliver-page tools on *mcp*."""

    # ------------------------------------------------------------------
    # Formats & codecs
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_formats() -> dict:
        """Return available render formats as {formatName: description}.

        Use the format names as input for render_get_codecs() or
        render_set_format_and_codec().
        """
        try:
            _api, project = _require_project()
            # GetRenderFormats() returns {name: description, ...}
            formats: dict = project.GetRenderFormats() or {}
            return formats
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_formats", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_codecs(format_name: str) -> dict:
        """Return available codecs for a given render format.

        Args:
            format_name: The render format name (e.g. "QuickTime", "mp4").
                         Get valid names from render_get_formats().

        Returns:
            A dict of {codecName: description} for the specified format.
        """
        try:
            _api, project = _require_project()
            # GetRenderCodecs() returns {name: description} for the format
            codecs: dict = project.GetRenderCodecs(format_name) or {}
            return codecs
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_codecs", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_presets() -> list[str]:
        """List all saved render preset names.

        Returns:
            A list of preset name strings that can be passed to
            render_load_preset().
        """
        try:
            _api, project = _require_project()
            # GetRenderPresetList() returns a list of preset name strings
            presets: list[str] = project.GetRenderPresetList() or []
            return presets
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_presets", str(exc)
            ) from exc

    @mcp.tool()
    def render_load_preset(preset_name: str) -> bool:
        """Load a render preset by name, applying its settings.

        Args:
            preset_name: Exact name of the preset.  Get valid names from
                         render_get_presets().

        Returns:
            True if the preset was loaded successfully.
        """
        try:
            _api, project = _require_project()
            # LoadRenderPreset() returns True on success
            result: bool = project.LoadRenderPreset(preset_name)
            if not result:
                raise ResolveOperationFailed(
                    "render_load_preset",
                    f"Could not load preset '{preset_name}'. "
                    "Check the name matches an existing preset.",
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
                "render_load_preset", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Render settings
    # ------------------------------------------------------------------

    @mcp.tool()
    def render_set_settings(settings: dict) -> bool:
        """Apply render settings from a dictionary.

        Args:
            settings: A dict of render setting key-value pairs.  Valid keys:
                      TargetDir, CustomName, FormatWidth, FormatHeight,
                      FrameRate, MarkIn, MarkOut, AudioCodec, AudioBitDepth,
                      AudioSampleRate, ExportAlpha.

        Returns:
            True if all settings were applied successfully.
        """
        # Validate keys before hitting the API to give clear feedback
        invalid_keys = set(settings.keys()) - _VALID_RENDER_SETTING_KEYS
        if invalid_keys:
            raise ResolveOperationFailed(
                "render_set_settings",
                f"Invalid setting keys: {', '.join(sorted(invalid_keys))}. "
                f"Valid keys: {', '.join(sorted(_VALID_RENDER_SETTING_KEYS))}",
            )

        try:
            _api, project = _require_project()
            # SetRenderSettings() returns True on success
            result: bool = project.SetRenderSettings(settings)
            if not result:
                raise ResolveOperationFailed(
                    "render_set_settings",
                    "Resolve rejected the render settings. "
                    "Check that all values are valid for the current format.",
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
                "render_set_settings", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Format & codec (current)
    # ------------------------------------------------------------------

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_format_and_codec() -> dict:
        """Return the currently selected render format and codec.

        Returns:
            A dict with keys "format" and "codec" (both strings).
        """
        try:
            _api, project = _require_project()
            # GetCurrentRenderFormatAndCodec() returns {"format": ..., "codec": ...}
            info: dict = project.GetCurrentRenderFormatAndCodec() or {}
            return {
                "format": info.get("format", ""),
                "codec": info.get("codec", ""),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_format_and_codec", str(exc)
            ) from exc

    @mcp.tool()
    def render_set_format_and_codec(format_name: str, codec_name: str) -> bool:
        """Set the render format and codec.

        Args:
            format_name: The format name (e.g. "QuickTime").
            codec_name: The codec name within that format (e.g. "H.265").
                        Get valid combinations from render_get_formats() and
                        render_get_codecs().

        Returns:
            True if the format and codec were set successfully.
        """
        try:
            _api, project = _require_project()
            # SetCurrentRenderFormatAndCodec() returns True on success
            result: bool = project.SetCurrentRenderFormatAndCodec(
                format_name, codec_name
            )
            if not result:
                raise ResolveOperationFailed(
                    "render_set_format_and_codec",
                    f"Resolve rejected format '{format_name}' / "
                    f"codec '{codec_name}'. Verify the combination is valid.",
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
                "render_set_format_and_codec", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Job queue management
    # ------------------------------------------------------------------

    @mcp.tool()
    def render_add_job() -> str:
        """Add the current timeline to the render queue with current settings.

        The timeline must be set (Deliver page) and render settings must be
        configured before calling this tool.

        Returns:
            The job ID string for the newly queued render job.
        """
        try:
            _api, project = _require_project()
            # AddRenderJob() returns a job ID string or empty string on failure
            job_id: str = project.AddRenderJob()
            if not job_id:
                raise ResolveOperationFailed(
                    "render_add_job",
                    "Could not add render job. Ensure a timeline is open "
                    "and render settings are configured.",
                )
            return job_id
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_add_job", str(exc)
            ) from exc

    @mcp.tool(annotations={"destructiveHint": True})
    def render_delete_job(job_id: str) -> bool:
        """Delete a specific render job from the queue.

        Args:
            job_id: The job ID string returned by render_add_job() or
                    found in render_get_jobs() results.

        Returns:
            True if the job was deleted.
        """
        try:
            _api, project = _require_project()
            # DeleteRenderJob() returns True on success
            result: bool = project.DeleteRenderJob(job_id)
            if not result:
                raise ResolveOperationFailed(
                    "render_delete_job",
                    f"Could not delete render job '{job_id}'. "
                    "Verify the job ID is correct and the job exists.",
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
                "render_delete_job", str(exc)
            ) from exc

    @mcp.tool(annotations={"destructiveHint": True})
    def render_delete_all_jobs() -> bool:
        """Delete all render jobs from the queue.

        Returns:
            True if all jobs were deleted successfully.
        """
        try:
            _api, project = _require_project()
            # DeleteAllRenderJobs() returns True on success
            result: bool = project.DeleteAllRenderJobs()
            if not result:
                raise ResolveOperationFailed(
                    "render_delete_all_jobs",
                    "Resolve could not clear the render queue.",
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
                "render_delete_all_jobs", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_jobs() -> list[dict]:
        """Return all render jobs in the queue with their current status.

        Returns:
            A list of dicts, each with keys: job_id, status, timeline_name,
            target_dir, output_filename.
        """
        try:
            _api, project = _require_project()
            # GetRenderJobList() returns a list of dicts with Resolve's internal keys
            raw_jobs: list[dict] = project.GetRenderJobList() or []
            # Normalise key names to a consistent, lowercase convention
            return [
                {
                    "job_id": j.get("JobId", ""),
                    "status": j.get("RenderStatus", ""),
                    "timeline_name": j.get("TimelineName", ""),
                    "target_dir": j.get("TargetDir", ""),
                    "output_filename": j.get("OutputFilename", ""),
                }
                for j in raw_jobs
            ]
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_jobs", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # Render execution
    # ------------------------------------------------------------------

    @mcp.tool()
    def render_start(
        job_ids: list[str] | None = None,
        is_interactive: bool = False,
    ) -> bool:
        """Start rendering queued jobs.

        Args:
            job_ids: Optional list of specific job IDs to render.  If None,
                     all queued jobs are rendered.
            is_interactive: If True, rendering will show the visual preview
                            in Resolve (slower but useful for monitoring).

        Returns:
            True if rendering started successfully.
        """
        try:
            _api, project = _require_project()
            # StartRendering() accepts either specific job IDs or renders all
            if job_ids:
                result: bool = project.StartRendering(job_ids, is_interactive)
            else:
                result = project.StartRendering(
                    isInteractiveMode=is_interactive
                )
            if not result:
                raise ResolveOperationFailed(
                    "render_start",
                    "Resolve could not start rendering. "
                    "Ensure there are queued jobs and settings are valid.",
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
                "render_start", str(exc)
            ) from exc

    @mcp.tool()
    def render_stop() -> bool:
        """Stop the currently running render.

        Returns:
            True if rendering was stopped.  Also returns True if no render
            was in progress (idempotent).
        """
        try:
            _api, project = _require_project()
            # StopRendering() halts any active render; no return value
            project.StopRendering()
            return True
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_stop", str(exc)
            ) from exc

    @mcp.tool(annotations={"readOnlyHint": True})
    def render_get_status(job_id: str) -> dict:
        """Return the render progress for a specific job.

        Args:
            job_id: The job ID to check.

        Returns:
            A dict with keys: job_id (str), status (str),
            progress (int, 0-100), time_remaining (int, milliseconds).
        """
        try:
            _api, project = _require_project()
            # GetRenderJobStatus() returns a dict with Resolve's internal keys
            raw: dict = project.GetRenderJobStatus(job_id) or {}
            return {
                "job_id": job_id,
                "status": raw.get("JobStatus", ""),
                "progress": raw.get("CompletionPercentage", 0),
                "time_remaining": raw.get("EstimatedTimeRemainingInMs", 0),
            }
        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "render_get_status", str(exc)
            ) from exc
