"""OAuth 2.0 response models."""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """OAuth 2.0 token response model.
    
    As specified in RFC 6749 Section 5.1.
    """
    
    access_token: str = Field(
        ...,
        description="The access token issued by the authorization server"
    )
    token_type: str = Field(
        default="Bearer",
        description="The type of token issued (always 'Bearer')"
    )
    expires_in: int = Field(
        ...,
        description="The lifetime in seconds of the access token",
        gt=0
    )
    scope: str = Field(
        ...,
        description="Space-separated list of granted scopes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "device-identifier:retrieve-identifier location-retrieval:read"
            }
        }


class TokenRevocationResponse(BaseModel):
    """Token revocation response model."""
    
    message: str = Field(
        default="Token revoked successfully",
        description="Confirmation message"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Token revoked successfully"
            }
        }
