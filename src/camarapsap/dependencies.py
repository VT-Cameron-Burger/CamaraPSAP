"""FastAPI dependencies for authentication and authorization."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .services.authorization import AuthorizationService
from .models.auth import AccessToken, Scope


# HTTP Bearer token security scheme
security = HTTPBearer()

# Shared authorization service instance
auth_service = AuthorizationService()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AccessToken:
    """
    Extract and validate the current access token from the Authorization header.
    
    Args:
        credentials: The HTTP Bearer credentials from the request
    
    Returns:
        AccessToken: The validated access token
    
    Raises:
        HTTPException: 401 if token is invalid, expired, or revoked
    """
    token = credentials.credentials
    
    access_token = await auth_service.validate_token(token)
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return access_token


def require_scope(required_scope: Scope):
    """
    Create a dependency that requires a specific scope.
    
    Args:
        required_scope: The scope that must be present in the token
    
    Returns:
        A dependency function that validates the scope
    """
    async def scope_checker(token: AccessToken = Depends(get_current_token)) -> AccessToken:
        if not token.has_scope(required_scope.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Token missing required scope: {required_scope.value}",
            )
        return token
    
    return scope_checker


async def get_current_token_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[AccessToken]:
    """
    Extract and validate the access token if present (optional authentication).
    
    Args:
        credentials: The HTTP Bearer credentials from the request (optional)
    
    Returns:
        AccessToken if valid token provided, None otherwise
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return await auth_service.validate_token(token)
