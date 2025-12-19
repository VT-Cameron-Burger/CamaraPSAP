"""Device Identifier models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from ..common.device import Device, DeviceResponse


class RequestBody(BaseModel):
    """Common request body to allow optional Device object to be passed."""
    
    device: Optional[Device] = Field(
        None,
        description="Device identification when using 2-legged access token"
    )


class CommonResponseBody(BaseModel):
    """Common parameters to be included in all responses."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    last_checked: datetime = Field(
        ...,
        alias="lastChecked",
        description="Timestamp when the information was last confirmed to be correct"
    )
    device: Optional[DeviceResponse] = Field(
        None,
        description="Device identifier used by the implementation (for 2-legged tokens)"
    )


class DeviceIdentifier(CommonResponseBody):
    """The individual physical mobile device identifier, as expressed by the IMEI and IMEISV."""
    
    imei: str = Field(
        ...,
        pattern=r'^\d{15}$',
        description="International Mobile Equipment Identity (15 digits)"
    )
    imeisv: Optional[str] = Field(
        None,
        pattern=r'^\d{16}$',
        description="IMEI with Software Version (16 digits)"
    )
    tac: Optional[str] = Field(
        None,
        pattern=r'^\d{8}$',
        description="Type Allocation Code (first 8 digits of IMEI)"
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Device manufacturer name"
    )
    model: Optional[str] = Field(
        None,
        description="Device model name"
    )


class DeviceType(CommonResponseBody):
    """The physical device type, as expressed by Type Approval Code, manufacturer name and model name."""
    
    tac: str = Field(
        ...,
        pattern=r'^\d{8}$',
        description="Type Allocation Code (first 8 digits of IMEI)"
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Device manufacturer name"
    )
    model: Optional[str] = Field(
        None,
        description="Device model name"
    )


class DevicePPID(CommonResponseBody):
    """The individual physical mobile device identifier, expressed as a PPID (Pairwise Pseudonymous Identifier)."""
    
    ppid: str = Field(
        ...,
        description="Pairwise Pseudonymous Identifier - unique to but persistent for a given API consumer"
    )
