"""Latitude and Longitude coordinate models."""

from pydantic import BaseModel, Field


class Latitude(BaseModel):
    """Latitude component of a location."""
    
    value: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude value in degrees"
    )


class Longitude(BaseModel):
    """Longitude component of location."""
    
    value: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude value in degrees"
    )
