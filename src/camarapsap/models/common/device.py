"""Device model."""

from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from .phone_number import PhoneNumber
from .network_access_identifier import NetworkAccessIdentifier
from .device_ipv4 import DeviceIpv4Addr
from .device_ipv6 import DeviceIpv6Address


class Device(BaseModel):
    """End-user device able to connect to a mobile network.
    
    Examples of devices include smartphones or IoT sensors/actuators.
    
    The developer can choose to provide the below specified device identifiers:
    - ipv4Address
    - ipv6Address
    - phoneNumber
    - networkAccessIdentifier
    
    NOTE1: the API provider might support only a subset of these options. The API 
    consumer can provide multiple identifiers to be compatible across different API 
    providers. In this case the identifiers MUST belong to the same device.
    
    NOTE2: as for this Commonalities release, we are enforcing that the 
    networkAccessIdentifier is only part of the schema for future-proofing, and 
    CAMARA does not currently allow its use.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    phone_number: Optional[str] = Field(
        None,
        alias="phoneNumber",
        pattern=r'^\+[1-9][0-9]{4,14}$',
        examples=["+123456789"],
        description="Phone number in E.164 format"
    )
    network_access_identifier: Optional[str] = Field(
        None,
        alias="networkAccessIdentifier",
        examples=["123456789@domain.com"],
        description="Network access identifier"
    )
    ipv4_address: Optional[DeviceIpv4Addr] = Field(
        None,
        alias="ipv4Address",
        description="IPv4 address configuration"
    )
    ipv6_address: Optional[str] = Field(
        None,
        alias="ipv6Address",
        examples=["2001:db8:85a3:8d3:1319:8a2e:370:7344"],
        description="IPv6 address"
    )
    
    @model_validator(mode='after')
    def check_at_least_one_identifier(self) -> 'Device':
        if not any([
            self.phone_number,
            self.network_access_identifier,
            self.ipv4_address,
            self.ipv6_address
        ]):
            raise ValueError('At least one device identifier must be provided')
        return self


class DeviceResponse(Device):
    """An identifier for the end-user equipment able to connect to the network 
    that the response refers to.
    
    This parameter is only returned when the API consumer includes the `device` 
    parameter in their request (i.e. they are using a two-legged access token), 
    and is relevant when more than one device identifier is specified, as only one 
    of those device identifiers is allowed in the response.
    """
    
    @model_validator(mode='after')
    def check_max_one_identifier(self) -> 'DeviceResponse':
        identifiers = sum([
            self.phone_number is not None,
            self.network_access_identifier is not None,
            self.ipv4_address is not None,
            self.ipv6_address is not None
        ])
        if identifiers > 1:
            raise ValueError('DeviceResponse must contain at most one identifier')
        return self
