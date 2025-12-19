"""Point and coordinate models."""

from pydantic import BaseModel, Field, ConfigDict


class Point(BaseModel):
    """Coordinates (latitude, longitude) defining a location in a map."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": 50.735851,
                "longitude": 7.10066
            }
        }
    )
    
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        examples=[50.735851],
        description="Latitude component of a location"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        examples=[7.10066],
        description="Longitude component of location"
    )
