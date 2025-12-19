"""Network Access Identifier model."""

from pydantic import BaseModel, Field


class NetworkAccessIdentifier(BaseModel):
    """A public identifier addressing a subscription in a mobile network.
    
    In 3GPP terminology, it corresponds to the GPSI formatted with the External 
    Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, 
    the network access identifier is not subjected to portability ruling in force, 
    and is individually managed by each operator.
    """
    
    network_access_identifier: str = Field(
        ...,
        examples=["123456789@domain.com"],
        description="Network access identifier in format localId@domain"
    )
