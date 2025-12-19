"""OAuth 2.0 token endpoint for issuing access tokens."""

from fastapi import APIRouter, HTTPException, Form, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .services.authorization import AuthorizationService
from .services.client import ClientService
from .models.error_models.camara_errors import Error400, Error401
from .models.auth import Scope, TokenResponse, TokenRevocationResponse
from .db.database import get_db


router = APIRouter(
    prefix="/oauth",
    tags=["OAuth 2.0 Authentication"]
)

# Shared authorization service instance
auth_service = AuthorizationService()


@router.post(
    "/token",
    response_model=TokenResponse,
    responses={
        400: {"model": Error400, "description": "Bad Request - Invalid parameters"},
        401: {"model": Error401, "description": "Unauthorized - Invalid client credentials"},
    }
)
async def token_endpoint(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form(None),
    code: str = Form(None),  # For authorization_code flow
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    OAuth 2.0 token endpoint for obtaining access tokens.
    
    Supports two grant types:
    - client_credentials: For 2-legged (server-to-server) authentication
    - authorization_code: For 3-legged (user-consented) authentication (NOT YET SUPPORTED)
    
    **Request Body (application/x-www-form-urlencoded):**
    
    For client_credentials:
    - grant_type: "client_credentials"
    - client_id: Your application client ID
    - client_secret: Your application client secret
    - scope: Space-separated list of requested scopes
    
    For authorization_code (NOT YET SUPPORTED):
    - grant_type: "authorization_code"
    - client_id: Your application client ID
    - client_secret: Your application client secret
    - code: Authorization code from user consent flow
    - scope: Space-separated list of requested scopes
    
    **Example Response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "device-identifier:retrieve-identifier location-retrieval:read"
    }
    ```
    
    **Example Request (client_credentials):**
    ```bash
    curl -X POST http://localhost:8000/oauth/token \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "grant_type=client_credentials" \\
      -d "client_id=my_application" \\
      -d "client_secret=my_secret" \\
      -d "scope=device-identifier:retrieve-identifier location-retrieval:read"
    ```
    
    **Example Request (authorization_code) - NOT YET SUPPORTED:**
    ```bash
    curl -X POST http://localhost:8000/oauth/token \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "grant_type=authorization_code" \\
      -d "client_id=my_application" \\
      -d "client_secret=my_secret" \\
      -d "code=auth_code_xyz" \\
      -d "scope=location-verification:verify"
    ```
    """
    
    # Validate grant_type
    if grant_type not in ["client_credentials", "authorization_code"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant_type: {grant_type}. Must be 'client_credentials' or 'authorization_code'"
        )
    
    # Parse requested scopes
    scopes = scope.split() if scope else []
    
    # Validate scopes format
    valid_scopes = [s.value for s in Scope]
    invalid_scopes = [s for s in scopes if s not in valid_scopes]
    if invalid_scopes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scopes: {', '.join(invalid_scopes)}"
        )
    
    # Authenticate client credentials
    client = await ClientService.authenticate_client(db, client_id, client_secret)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate that client is allowed to request these scopes
    if not await ClientService.validate_scopes(client, scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client not authorized for requested scopes. Allowed scopes: {', '.join(client.allowed_scopes)}"
        )
    
    # Handle client_credentials flow (2-legged)
    if grant_type == "client_credentials":
        try:
            access_token = await auth_service.create_two_legged_token(
                client_id=client_id,
                scopes=scopes
            )
            token_dict = access_token.to_dict()
            return TokenResponse(**token_dict)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create token: {str(e)}"
            )
    
    # Handle authorization_code flow (3-legged)
    elif grant_type == "authorization_code":
        # 3-legged OAuth flow not yet implemented
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "code": "NOT_IMPLEMENTED",
                "message": "Authorization code flow (3-legged authentication) is not yet implemented. Please use client_credentials grant type."
            }
        )
    
    # Should never reach here, but satisfies return type checker
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid grant_type"
    )


@router.post(
    "/revoke",
    response_model=TokenRevocationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error400, "description": "Bad Request - Invalid token"},
    }
)
async def revoke_token_endpoint(
    token: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    db: AsyncSession = Depends(get_db)
) -> TokenRevocationResponse:
    """
    Revoke an access token.
    
    This endpoint allows clients to revoke tokens (e.g., on user logout).
    
    **Request Body (application/x-www-form-urlencoded):**
    - token: The access token to revoke
    - client_id: Your application client ID
    - client_secret: Your application client secret
    
    **Example Request:**
    ```bash
    curl -X POST http://localhost:8000/oauth/revoke \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \\
      -d "client_id=my_application" \\
      -d "client_secret=my_secret"
    ```
    """
    
    # Authenticate client credentials
    client = await ClientService.authenticate_client(db, client_id, client_secret)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials"
        )
    
    # Revoke the token
    success = await auth_service.revoke_token(token)
    
    if not success:
        # Per OAuth 2.0 spec, revocation endpoint should succeed even if token is invalid
        # This prevents token scanning attacks
        pass
    
    return TokenRevocationResponse()
