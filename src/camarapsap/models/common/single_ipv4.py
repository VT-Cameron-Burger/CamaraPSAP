"""Single IPv4 address model."""

from pydantic import BaseModel, Field, field_validator
import ipaddress


class SingleIpv4Addr(BaseModel):
    """A single IPv4 address with no subnet mask."""
    
    address: str = Field(
        ...,
        examples=["84.125.93.10"],
        description="IPv4 address"
    )
    
    @field_validator('address')
    @classmethod
    def validate_ipv4(cls, v: str) -> str:
        try:
            ipaddress.IPv4Address(v)
        except ValueError:
            raise ValueError(f'Invalid IPv4 address: {v}')
        return v
