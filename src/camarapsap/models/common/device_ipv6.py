"""Device IPv6 address model."""

from pydantic import BaseModel, Field, field_validator
import ipaddress


class DeviceIpv6Address(BaseModel):
    """The device should be identified by the observed IPv6 address, or by any 
    single IPv6 address from within the subnet allocated to the device 
    (e.g. adding ::0 to the /64 prefix).
    """
    
    ipv6_address: str = Field(
        ...,
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        description="IPv6 address"
    )
    
    @field_validator('ipv6_address')
    @classmethod
    def validate_ipv6(cls, v: str) -> str:
        try:
            ipaddress.IPv6Address(v)
        except ValueError:
            raise ValueError(f'Invalid IPv6 address: {v}')
        return v
