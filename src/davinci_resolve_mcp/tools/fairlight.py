"""Fairlight audio tools — insert audio, list and apply presets.

Provides a minimal set of tools for the Fairlight audio workspace in
DaVinci Resolve.  The Resolve scripting API exposes very limited audio
functionality compared to the visual editing or color grading domains,
so these tools wrap the few available operations defensively.

NOTE: Most Fairlight-specific scripting methods are only available in
DaVinci Resolve Studio 18+ and may not exist in the free edition.
Every API call is wrapped in try/except so that unsupported operations
return a clear error rather than crashing the server.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ..exceptions import ResolveNotRunning, ResolveOperationFailed
from ..resolve_api import ResolveAPI


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(mcp: FastMCP) -> None:
    """Register all Fairlight audio tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # 1. Insert an audio file at the playhead position
    # ------------------------------------------------------------------
    @mcp.tool()
    def fairlight_insert_audio(file_path: str, track_index: int = 1) -> bool:
        """Import an audio file and insert it into the timeline on an audio track.

        The file is first imported into the Media Pool, then appended to the
        current timeline.  Because the scripting API has limited control over
        audio-track targeting, the clip is appended using the standard
        AppendToTimeline method.

        Args:
            file_path:   Absolute path to the audio file (WAV, MP3, AAC, etc.).
            track_index: 1-based audio track index hint.  The Resolve API may
                         not honour this directly — the clip will be placed on
                         the first available audio track.

        Returns True if the audio was inserted successfully.
        """
        try:
            api = ResolveAPI.get_instance()

            # Ensure a timeline exists to insert audio into
            timeline = api.timeline
            if timeline is None:
                raise ResolveOperationFailed(
                    "fairlight_insert_audio",
                    "No timeline is currently open. Create or open a timeline first.",
                )

            # Step 1: Import the audio file into the Media Pool
            pool = api.media_pool
            if pool is None:
                raise ResolveOperationFailed(
                    "fairlight_insert_audio",
                    "Media Pool is not available. Is a project open?",
                )

            imported = pool.ImportMedia([file_path])
            if not imported:
                raise ResolveOperationFailed(
                    "fairlight_insert_audio",
                    f"Failed to import audio file '{file_path}'. "
                    "Check that the file exists and is a supported audio format.",
                )

            # Step 2: Append the imported clip to the current timeline.
            # AppendToTimeline places clips at the end of the timeline on
            # appropriate tracks.  For audio-only files, Resolve routes them
            # to audio tracks automatically.
            #
            # We also attempt SetTrackIndex if the API supports it, to
            # honour the caller's track preference.
            clip_info = [{"mediaPoolItem": item} for item in imported]

            # Try the extended signature with track targeting first
            try:
                # Some Resolve versions support a dict with "trackIndex"
                for info in clip_info:
                    info["trackIndex"] = track_index
                    info["mediaType"] = 2  # 2 = audio in some API versions

                result = pool.AppendToTimeline(clip_info)
            except (TypeError, AttributeError):
                # Fall back to the simple list-of-items approach
                result = pool.AppendToTimeline(imported)

            if not result:
                raise ResolveOperationFailed(
                    "fairlight_insert_audio",
                    "Imported the audio file but failed to append it to the timeline.",
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
                "fairlight_insert_audio", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 2. List available Fairlight presets
    # ------------------------------------------------------------------
    @mcp.tool(annotations={"readOnlyHint": True})
    def fairlight_get_presets() -> list[str]:
        """List available Fairlight audio effect presets.

        Returns preset names as strings.  Returns an empty list if the
        Fairlight preset API is not available in this Resolve version.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "fairlight_get_presets",
                    "No project is currently open.",
                )

            # GetFairlightPresetList is non-standard and may not exist
            # in all Resolve versions.  Return an empty list gracefully.
            try:
                presets = project.GetFairlightPresetList()
            except AttributeError:
                return []

            if not presets:
                return []

            # The API may return a list of strings or a list of dicts.
            # Normalise to a plain list of names.
            if isinstance(presets[0], dict):
                return [p.get("Name", str(p)) for p in presets]
            return [str(p) for p in presets]

        except (ResolveNotRunning, ResolveOperationFailed):
            raise
        except AttributeError as exc:
            raise ResolveNotRunning(
                f"Lost connection to Resolve (stale reference: {exc}). Please retry."
            ) from exc
        except Exception as exc:
            raise ResolveOperationFailed(
                "fairlight_get_presets", str(exc)
            ) from exc

    # ------------------------------------------------------------------
    # 3. Apply a Fairlight preset to a track
    # ------------------------------------------------------------------
    @mcp.tool()
    def fairlight_apply_preset(preset_name: str, track_index: int = 1) -> bool:
        """Apply a Fairlight audio effect preset to an audio track.

        Args:
            preset_name: Exact name of the preset (from fairlight_get_presets).
            track_index: 1-based audio track index to apply the preset to
                         (default 1).  The API may apply the preset globally
                         if per-track targeting is not supported.

        Returns True if the preset was applied successfully.
        This method may not be available in all Resolve versions.
        """
        try:
            api = ResolveAPI.get_instance()
            project = api.project
            if project is None:
                raise ResolveOperationFailed(
                    "fairlight_apply_preset",
                    "No project is currently open.",
                )

            # Try applying with a track_index argument first (some versions
            # support per-track targeting), then fall back to global application.
            applied = False

            try:
                result = project.ApplyFairlightPreset(preset_name, track_index)
                if result:
                    applied = True
            except TypeError:
                # Two-argument version not supported — try single-argument
                pass
            except AttributeError as exc:
                raise ResolveOperationFailed(
                    "fairlight_apply_preset",
                    "ApplyFairlightPreset() is not available in this Resolve version.",
                ) from exc

            if not applied:
                try:
                    result = project.ApplyFairlightPreset(preset_name)
                    if result:
                        applied = True
                except AttributeError as exc:
                    raise ResolveOperationFailed(
                        "fairlight_apply_preset",
                        "ApplyFairlightPreset() is not available in this Resolve version.",
                    ) from exc

            if not applied:
                raise ResolveOperationFailed(
                    "fairlight_apply_preset",
                    f"Failed to apply Fairlight preset '{preset_name}'. "
                    "Verify the preset name is correct (use fairlight_get_presets).",
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
                "fairlight_apply_preset", str(exc)
            ) from exc
