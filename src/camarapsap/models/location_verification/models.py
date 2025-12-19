"""Location Verification models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
from ..common.device import Device, DeviceResponse
from ..location_retrieval.models import Area, Circle


class VerificationResult(str, Enum):
    """Result of a verification request.
    
    - TRUE: when the network locates the device within the requested area
    - FALSE: when the requested area does not match the area where the network locates the device
    - PARTIAL: when the requested area partially matches the area where the network locates the device
    """
    
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIAL = "PARTIAL"


class VerifyLocationRequest(BaseModel):
    """Request to verify the location of a device.
    
    Device is not required when using a 3-legged access token, following the rules 
    in the description.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    device: Optional[Device] = Field(
        None,
        description="Device identification (required for 2-legged access token)"
    )
    area: Area = Field(
        ...,
        description="Area to verify the device location against"
    )
    max_age: Optional[int] = Field(
        None,
        alias="maxAge",
        ge=0,
        examples=[120],
        description="Maximum age of location information in seconds. Absence means 'any age', 0 means fresh calculation"
    )


class VerifyLocationResponse(BaseModel):
    """Response to a location verification request."""
    
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    
    verification_result: VerificationResult = Field(
        ...,
        alias="verificationResult",
        description="Result of the verification"
    )
    last_location_time: datetime = Field(
        ...,
        alias="lastLocationTime",
        description="Timestamp of the last location information"
    )
    match_rate: Optional[int] = Field(
        None,
        alias="matchRate",
        ge=1,
        le=99,
        description="Estimation of match rate as percentage. Included only if verificationResult is PARTIAL"
    )
    device: Optional[DeviceResponse] = Field(
        None,
        description="Device identifier used by the implementation (for 2-legged tokens)"
    )
