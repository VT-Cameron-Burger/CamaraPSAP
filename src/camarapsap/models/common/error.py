"""Error models."""

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    """Common schema for errors."""
    
    status: int = Field(
        ...,
        description="HTTP response status code"
    )
    code: str = Field(
        ...,
        description="A human-readable code to describe the error"
    )
    message: str = Field(
        ...,
        description="A human-readable description of what the event represents"
    )
