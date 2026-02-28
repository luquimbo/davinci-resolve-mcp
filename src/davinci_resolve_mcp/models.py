"""Pydantic models for structured tool inputs and outputs.

Only models that are actively used by tool modules live here.
"""

from pydantic import BaseModel, Field, field_validator


class CDLValues(BaseModel):
    """ASC-CDL color correction values (used by color.py tools)."""

    slope: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB slope")
    offset: list[float] = Field(default=[0.0, 0.0, 0.0], description="RGB offset")
    power: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB power")
    saturation: float = Field(default=1.0, ge=0.0, description="Saturation multiplier")

    @field_validator("slope", "offset", "power")
    @classmethod
    def must_be_rgb_triple(cls, v: list[float]) -> list[float]:
        """Ensure each RGB channel list contains exactly 3 elements."""
        if len(v) != 3:
            raise ValueError(f"Expected exactly 3 RGB values, got {len(v)}")
        return v
