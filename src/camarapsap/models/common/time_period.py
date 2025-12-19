"""Time period model."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TimePeriod(BaseModel):
    """Time period with start and optional end date."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    start_date: datetime = Field(
        ...,
        alias="startDate",
        description="An instant of time, starting of the TimePeriod. Must follow RFC 3339 and must have time zone"
    )
    end_date: Optional[datetime] = Field(
        None,
        alias="endDate",
        description="An instant of time, ending of the TimePeriod. If not included, then the period has no ending date. Must follow RFC 3339 and must have time zone"
    )
