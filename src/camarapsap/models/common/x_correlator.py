"""X-Correlator header model."""

from pydantic import BaseModel, Field


class XCorrelator(BaseModel):
    """Correlation id for the different services."""
    
    x_correlator: str = Field(
        ...,
        pattern=r'^[a-zA-Z0-9-_:;.\/<>{}]{0,256}$',
        examples=["b4333c46-49c0-4f62-80d7-f0ef930f1c46"],
        description="Correlation id for the different services"
    )
