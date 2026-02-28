"""Pydantic models for structured tool inputs and outputs.

Only models that are actively used by tool modules live here.
"""

from pydantic import BaseModel, Field


class CDLValues(BaseModel):
    """ASC-CDL color correction values (used by color.py tools)."""

    slope: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB slope")
    offset: list[float] = Field(default=[0.0, 0.0, 0.0], description="RGB offset")
    power: list[float] = Field(default=[1.0, 1.0, 1.0], description="RGB power")
    saturation: float = Field(default=1.0, description="Saturation multiplier")
