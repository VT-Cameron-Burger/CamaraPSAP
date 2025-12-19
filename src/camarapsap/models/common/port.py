"""Port number model."""

from pydantic import BaseModel, Field


class Port(BaseModel):
    """TCP or UDP port number."""
    
    port: int = Field(
        ...,
        ge=0,
        le=65535,
        description="TCP or UDP port number"
    )
