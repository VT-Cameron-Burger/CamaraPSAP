"""Point list model for polygons."""

from pydantic import BaseModel, Field, field_validator
from typing import List
from .point import Point


class PointList(BaseModel):
    """List of points defining a polygon."""
    
    points: List[Point] = Field(
        ...,
        min_length=3,
        max_length=15,
        description="List of points defining a polygon"
    )
    
    @field_validator('points')
    @classmethod
    def validate_point_list(cls, v: List[Point]) -> List[Point]:
        if len(v) < 3:
            raise ValueError('Polygon must have at least 3 points')
        if len(v) > 15:
            raise ValueError('Polygon must have at most 15 points')
        return v
