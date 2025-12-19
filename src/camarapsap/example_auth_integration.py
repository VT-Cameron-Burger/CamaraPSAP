"""
Example: How to add authentication to API endpoints.

This file demonstrates how to integrate the JWT authorization system
with FastAPI endpoints using the authentication dependencies.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from .config import settings
from .dependencies import require_scope
from .models.auth import AccessToken, Scope
from .models.device_identifier import RequestBody, DeviceIdentifier
from .models.error_models.camara_errors import Error401, Error403


# Example router with authentication
router = APIRouter(
    prefix=f"/device-identifier/{settings.device_version_id}",
    tags=["Get Device Identifiers (Authenticated)"]
)


@router.post(
    "/retrieve-identifier",
    responses={
        401: {"model": Error401, "description": "Unauthorized - Invalid or missing token"},
        403: {"model": Error403, "description": "Forbidden - Insufficient permissions"},
    }
)
async def retrieve_identifier_with_auth(
    request: RequestBody,
    x_correlator: Optional[str] = Header(None, alias="x-correlator"),
    # Require authentication with specific scope
    token: AccessToken = Depends(require_scope(Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER))
) -> DeviceIdentifier:
    """
    Get device identifier (with authentication).
    
    This endpoint requires:
    - Valid JWT access token in Authorization header
    - Token must have 'device-identifier:retrieve-identifier' scope
    
    For 2-legged tokens:
        - Client must provide device identifiers in request body
    
    For 3-legged tokens:
        - Device identifiers are extracted from the token (user's authenticated device)
        - Request body device field is optional
    
    Example request headers:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        x-correlator: 550e8400-e29b-41d4-a716-446655440000
    """
    
    # Check token type to determine device identifier source
    if token.token_type.value == "3-legged":
        # For 3-legged tokens, use device info from token
        device_info = token.device_info
        if device_info:
            # Use authenticated device from token
            print(f"Using device from 3-legged token: {device_info}")
        elif request.device:
            # Fall back to request body if provided
            device_info = request.device.model_dump()
        else:
            raise HTTPException(
                status_code=400,
                detail="Device identifier required for 3-legged token without device context"
            )
    else:
        # For 2-legged tokens, device must be in request body
        if not request.device:
            raise HTTPException(
                status_code=400,
                detail="Device identifier required in request body for 2-legged tokens"
            )
        device_info = request.device.model_dump()
    
    # Your business logic here
    # ... query database, process device info, etc.
    
    # Mock response for demonstration
    from datetime import datetime
    from .models.common.device import DeviceResponse
    
    return DeviceIdentifier(
        imei="123456789012345",
        imeisv="1234567890123456",
        tac="12345678",
        manufacturer="ExampleManufacturer",
        model="ExampleModel",
        lastChecked=datetime.now(),
        device=DeviceResponse(
            phoneNumber="+1234567890",
            networkAccessIdentifier=None,
            ipv4Address=None,
            ipv6Address=None
        )
    )


# Example: How to create tokens (typically done in a separate auth endpoint)
"""
from .services.authorization import AuthorizationService
from .models.auth import Scope

auth_service = AuthorizationService()

# Create 2-legged token (client credentials flow)
two_legged_token = auth_service.create_two_legged_token(
    client_id="my_client_id",
    client_secret="my_client_secret",
    scopes=[
        Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value,
        Scope.LOCATION_RETRIEVAL_READ.value
    ]
)

# Create 3-legged token (authorization code flow - after user auth)
three_legged_token = auth_service.create_three_legged_token(
    client_id="my_client_id",
    authorization_code="auth_code_from_oauth_flow",
    scopes=[Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value],
    user_id="user_12345",
    device_info={
        "phoneNumber": "+1234567890",
        "ipv4Address": {"publicAddress": "192.0.2.1"}
    }
)

# Return token to client
return two_legged_token.to_dict()
# {
#     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#     "token_type": "Bearer",
#     "expires_in": 3600,
#     "scope": "device-identifier:retrieve-identifier location-retrieval:read"
# }
"""


# Example: How to test with curl
"""
# 1. Get a token (normally from OAuth endpoint)
# For testing, generate a token with test_jwt_simple.py

# 2. Use token in API request
curl -X POST http://localhost:8000/device-identifier/vwip/retrieve-identifier \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \\
  -H "Content-Type: application/json" \\
  -H "x-correlator: 550e8400-e29b-41d4-a716-446655440000" \\
  -d '{
    "device": {
      "phoneNumber": "+1234567890"
    }
  }'
"""
