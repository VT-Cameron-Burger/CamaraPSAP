"""Location Retrieval models."""

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, List, Literal, Union, Annotated
from datetime import datetime
from enum import Enum
from ..common.device import Device, DeviceResponse
from ..common.point import Point


class AreaType(str, Enum):
    """Type of area - CIRCLE or POLYGON."""
    
    CIRCLE = "CIRCLE"
    POLYGON = "POLYGON"


class Circle(BaseModel):
    """Circular area."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "areaType": "CIRCLE",
                "center": {
                    "latitude": 50.735851,
                    "longitude": 7.10066
                },
                "radius": 800
            }
        }
    )
    
    area_type: Literal["CIRCLE"] = Field(
        "CIRCLE",
        alias="areaType",
        description="Type of this area"
    )
    center: Point = Field(
        ...,
        description="Center point of the circle"
    )
    radius: int = Field(
        ...,
        gt=0,
        description="Radius of the circle in meters"
    )


class Polygon(BaseModel):
    """Polygonal area."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    area_type: Literal["POLYGON"] = Field(
        "POLYGON",
        alias="areaType",
        description="Type of this area"
    )
    boundary: List[Point] = Field(
        ...,
        min_length=3,
        max_length=15,
        description="List of points defining the polygon boundary"
    )
    
    @field_validator('boundary')
    @classmethod
    def validate_polygon_closed(cls, v: List[Point]) -> List[Point]:
        if len(v) < 3:
            raise ValueError('Polygon must have at least 3 points')
        if len(v) > 15:
            raise ValueError('Polygon must have at most 15 points')
        return v


# Union type for Area (no base class needed)
Area = Union[Circle, Polygon]


class RetrievalLocationRequest(BaseModel):
    """Request to retrieve the location of a device.
    
    Device is not required when using a 3-legged access token, following the rules 
    in the description.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    device: Optional[Device] = Field(
        None,
        description="Device identification (required for 2-legged access token)"
    )
    max_age: Optional[int] = Field(
        None,
        alias="maxAge",
        ge=0,
        description="Maximum age of location information in seconds. Absence means 'any age', 0 means fresh calculation"
    )
    max_surface: Optional[int] = Field(
        None,
        alias="maxSurface",
        gt=0,
        examples=[1000000],
        description="Maximum surface area in square meters that is acceptable"
    )


class Location(BaseModel):
    """Device location."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "lastLocationTime": "2023-10-17T13:18:23.682Z",
                "area": {
                    "areaType": "CIRCLE",
                    "center": {
                        "latitude": 50.735851,
                        "longitude": 7.10066
                    },
                    "radius": 800
                }
            }
        }
    )
    
    last_location_time: datetime = Field(
        ...,
        alias="lastLocationTime",
        description="Last date and time when the device was localized"
    )
    area: Annotated[Union[Circle, Polygon], Field(discriminator="area_type")] = Field(
        ...,
        description="Area where the device is located (Circle or Polygon)"
    )
    device: Optional[DeviceResponse] = Field(
        None,
        description="Device identifier used by the implementation (for 2-legged tokens)"
    )