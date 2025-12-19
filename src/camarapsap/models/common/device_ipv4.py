"""Device IPv4 address model."""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional
import ipaddress


class DeviceIpv4Addr(BaseModel):
    """The device should be identified by either the public (observed) IP address 
    and port as seen by the application server, or the private (local) and any 
    public (observed) IP addresses in use by the device.
    
    If the allocated and observed IP addresses are the same (i.e. NAT is not in use) 
    then the same address should be specified for both publicAddress and privateAddress.
    
    If NAT64 is in use, the device should be identified by its publicAddress and 
    publicPort, or separately by its allocated IPv6 address.
    
    In all cases, publicAddress must be specified, along with at least one of either 
    privateAddress or publicPort, dependent upon which is known. In general, mobile 
    devices cannot be identified by their public IPv4 address alone.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    public_address: str = Field(
        ...,
        alias="publicAddress",
        examples=["84.125.93.10"],
        description="Public IPv4 address"
    )
    private_address: Optional[str] = Field(
        None,
        alias="privateAddress",
        examples=["192.168.1.10"],
        description="Private IPv4 address"
    )
    public_port: Optional[int] = Field(
        None,
        alias="publicPort",
        ge=0,
        le=65535,
        examples=[59765],
        description="TCP or UDP port number"
    )
    
    @field_validator('public_address', 'private_address')
    @classmethod
    def validate_ipv4(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                ipaddress.IPv4Address(v)
            except ValueError:
                raise ValueError(f'Invalid IPv4 address: {v}')
        return v
    
    @model_validator(mode='after')
    def check_required_fields(self) -> 'DeviceIpv4Addr':
        if self.private_address is None and self.public_port is None:
            raise ValueError('Either privateAddress or publicPort must be provided')
        return self
