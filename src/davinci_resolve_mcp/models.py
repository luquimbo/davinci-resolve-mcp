"""Pydantic models for structured tool inputs and outputs."""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Marker
# ---------------------------------------------------------------------------
class MarkerInfo(BaseModel):
    """A single marker on a clip or timeline."""

    frame_id: int = Field(description="Frame number where the marker is placed")
    color: str = Field(description="Marker color (e.g. 'Blue', 'Red')")
    name: str = Field(default="", description="Short marker name")
    note: str = Field(default="", description="Extended marker note")
    duration: int = Field(default=1, description="Duration in frames")
    custom_data: str = Field(default="", description="Custom data string")


# ---------------------------------------------------------------------------
# Clip / Media Pool Item
# ---------------------------------------------------------------------------
class ClipInfo(BaseModel):
    """Summary of a Media Pool clip."""

    name: str
    clip_id: str = Field(default="", description="Internal clip identifier")
    file_path: str = Field(default="", description="Source file path on disk")
    duration: str = Field(default="", description="Duration as timecode string")
    fps: str = Field(default="", description="Clip frame rate")
    resolution: str = Field(default="", description="Resolution (e.g. '1920x1080')")
    codec: str = Field(default="", description="Video codec name")
    clip_color: str = Field(default="", description="Clip label color")


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------
class TimelineInfo(BaseModel):
    """Summary of a timeline."""

    name: str
    start_frame: int = Field(default=0)
    end_frame: int = Field(default=0)
    video_track_count: int = Field(default=0)
    audio_track_count: int = Field(default=0)
    start_timecode: str = Field(default="")


class TimelineItemInfo(BaseModel):
    """Summary of a single item (clip) on a timeline track."""

    name: str
    start: int = Field(description="Start frame on the timeline")
    end: int = Field(description="End frame on the timeline")
    duration: int = Field(description="Duration in frames")
    media_pool_item_name: str = Field(default="")
    track_type: str = Field(default="video")
    track_index: int = Field(default=1)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
class RenderSettings(BaseModel):
    """Settings for a render job. Only non-None fields are applied."""

    format_name: str | None = Field(default=None, description="e.g. 'mp4', 'mov'")
    codec_name: str | None = Field(default=None, description="e.g. 'H.264', 'H.265'")
    file_name: str | None = Field(default=None, description="Output file name (no extension)")
    target_dir: str | None = Field(default=None, description="Output directory path")
    mark_in: int | None = Field(default=None, description="Render start frame")
    mark_out: int | None = Field(default=None, description="Render end frame")
    audio_codec: str | None = Field(default=None, description="Audio codec name")
    audio_bit_depth: int | None = Field(default=None, description="Audio bit depth")
    audio_sample_rate: int | None = Field(default=None, description="Audio sample rate in Hz")
    export_alpha: bool | None = Field(default=None, description="Include alpha channel")
    quality: int | None = Field(default=None, description="Encoding quality (0–5 for some codecs)")


class RenderJobInfo(BaseModel):
    """Status of a render job."""

    job_id: str
    status: str = Field(description="'Ready', 'Rendering', 'Complete', 'Failed', 'Cancelled'")
    progress: float = Field(default=0.0, description="Completion percentage 0–100")
    timeline_name: str = Field(default="")
    target_dir: str = Field(default="")
    output_filename: str = Field(default="")
    render_time: str = Field(default="", description="Elapsed render time")


# ---------------------------------------------------------------------------
# Pagination wrapper
# ---------------------------------------------------------------------------
class PaginatedResult(BaseModel):
    """Generic paginated response for lists of items."""

    items: list = Field(default_factory=list)
    total: int = Field(default=0, description="Total items available")
    offset: int = Field(default=0, description="Current offset")
    limit: int = Field(default=50, description="Page size")
    has_more: bool = Field(default=False)


# ---------------------------------------------------------------------------
# Color grading (Phase 2)
# ---------------------------------------------------------------------------
class CDLValues(BaseModel):
    """ASC-CDL color correction values."""

    slope: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB slope")
    offset: list[float] = Field(default=[0.0, 0.0, 0.0], description="RGB offset")
    power: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB power")
    saturation: float = Field(default=1.0, description="Saturation multiplier")
