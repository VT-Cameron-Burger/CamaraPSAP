"""Location Retrieval API endpoints."""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime
from .config import settings
from .models.location_retrieval import (
    RetrievalLocationRequest,
    Location,
    Circle,
)
from .models.common import Point
from .models.error_models.camara_errors import (
    Error400,
    Error401,
    Error403,
    Error404,
    Error422,
)

router = APIRouter(
    prefix=f"/location-retrieval/{settings.location_version_id}",
    tags=["Location retrieval"]
)


@router.post(
    "/retrieve",
    responses={
        400: {"model": Error400, "description": "Bad Request"},
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
        404: {"model": Error404, "description": "Not Found"},
        422: {"model": Error422, "description": "Unprocessable Content"},
    }
)
async def retrieve_location(
    request: RetrievalLocationRequest,
    x_correlator: Optional[str] = Header(None, alias="x-correlator")
) -> Location:
    """
    Execute location retrieval for a user device.
    
    Retrieve the area where a certain user device is localized. The area can be
    described as a circle or polygon.
    
    Args:
        version_id: API version identifier
        request: Location retrieval request with optional device and constraints
        x_correlator: Correlation id for the different services
        
    Returns:
        Location information with area (Circle or Polygon) and timestamp
    """
    # Placeholder implementation - returns a circular area
    return Location(
        lastLocationTime=datetime.now(),
        area=Circle(
            areaType="CIRCLE",
            center=Point(
                latitude=50.735851,
                longitude=7.10066
            ),
            radius=800
        ),
        device=None
    )
