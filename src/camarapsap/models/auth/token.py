"""JWT access token models."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from ..common.device import Device


class TokenType(str, Enum):
    """Access token types."""
    TWO_LEGGED = "2-legged"
    THREE_LEGGED = "3-legged"


class Scope(str, Enum):
    """API scopes."""
    DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER = "device-identifier:retrieve-identifier"
    DEVICE_IDENTIFIER_RETRIEVE_TYPE = "device-identifier:retrieve-type"
    DEVICE_IDENTIFIER_RETRIEVE_PPID = "device-identifier:retrieve-ppid"
    LOCATION_RETRIEVAL_READ = "location-retrieval:read"
    LOCATION_VERIFICATION_VERIFY = "location-verification:verify"


class AccessToken(BaseModel):
    """Access token representation."""
    
    token: str = Field(..., description="JWT token string")
    token_type: TokenType = Field(..., description="Token type (2-legged or 3-legged)")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    scopes: list[str] = Field(default_factory=list, description="List of granted scopes")
    client_id: str = Field(..., description="Client application ID")
    user_id: Optional[str] = Field(None, description="User ID (3-legged tokens only)")
    device_info: Optional[Device] = Field(None, description="Device information (3-legged tokens only)")
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) >= self.expires_at
    
    def has_scope(self, scope: str) -> bool:
        """Check if token has required scope."""
        return scope in self.scopes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary format for API response."""
        return {
            "access_token": self.token,
            "token_type": "Bearer",
            "expires_in": int((self.expires_at - datetime.now(timezone.utc)).total_seconds()),
            "scope": " ".join(self.scopes),
        }
