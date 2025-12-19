"""Authorization service for generating and validating JWT access tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from redis import asyncio as aioredis
from ..config import settings
from ..models.auth.token import TokenType, AccessToken
from ..models.common.device import Device


class AuthorizationService:
    """Service for generating and validating JWT access tokens with Redis caching."""
    
    def __init__(self) -> None:
        # Redis client for revocation list and rate limiting
        self.redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    
    def _create_jwt_token(
        self,
        payload: dict[str, Any],
        expires_in_minutes: int
    ) -> str:
        """Create a JWT token with the given payload."""
        now = datetime.now(timezone.utc)
        payload.update({
            "iat": now,
            "exp": now + timedelta(minutes=expires_in_minutes),
            "iss": "camarapsap"
        })
        
        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return token
    
    async def create_two_legged_token(
        self,
        client_id: str,
        scopes: list[str],
        expires_in_minutes: Optional[int] = None
    ) -> AccessToken:
        """
        Create a 2-legged JWT access token (client credentials flow).
        
        2-legged tokens are used for server-to-server communication where
        the client needs to provide device identifiers in the API request.
        
        Args:
            client_id: The client application ID (already authenticated)
            scopes: List of requested scopes (already validated)
            expires_in_minutes: Token expiration time in minutes
        
        Returns:
            AccessToken: The generated JWT access token
        """
        if expires_in_minutes is None:
            expires_in_minutes = settings.jwt_access_token_expire_minutes
        
        payload = {
            "sub": client_id,
            "client_id": client_id,
            "token_type": TokenType.TWO_LEGGED.value,
            "scopes": scopes,
        }
        
        token_string = self._create_jwt_token(payload, expires_in_minutes)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        
        access_token = AccessToken(
            token=token_string,
            token_type=TokenType.TWO_LEGGED,
            expires_at=expires_at,
            scopes=scopes,
            client_id=client_id,
            user_id=None,
            device_info=None
        )
        
        return access_token
    
    async def create_three_legged_token(
        self,
        client_id: str,
        authorization_code: str,
        scopes: list[str],
        user_id: str,
        device_info: Optional[Device] = None,
        expires_in_minutes: Optional[int] = None
    ) -> AccessToken:
        """
        Create a 3-legged JWT access token (authorization code flow).
        
        3-legged tokens are used when the end user has authenticated and
        consented. The token contains user and device information, so
        device identifiers don't need to be provided in API requests.
        
        Args:
            client_id: The client application ID
            authorization_code: The authorization code from the auth flow
            scopes: List of requested scopes
            user_id: The authenticated user ID
            device_info: Device information associated with the user
            expires_in_minutes: Token expiration time in minutes
        
        Returns:
            AccessToken: The generated JWT access token
        """
        if expires_in_minutes is None:
            expires_in_minutes = settings.jwt_access_token_expire_minutes
        
        # In production, validate authorization_code and exchange it
        # for an access token after user authentication and consent
        
        payload: Dict[str, Any] = {
            "sub": user_id,
            "client_id": client_id,
            "token_type": TokenType.THREE_LEGGED.value,
            "scopes": scopes,
            "user_id": user_id,
        }
        
        if device_info:
            payload["device"] = device_info.model_dump()
        
        token_string = self._create_jwt_token(payload, expires_in_minutes)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        
        access_token = AccessToken(
            token=token_string,
            token_type=TokenType.THREE_LEGGED,
            expires_at=expires_at,
            scopes=scopes,
            client_id=client_id,
            user_id=user_id,
            device_info=device_info
        )
        
        return access_token
    
    async def validate_token(self, token: str) -> Optional[AccessToken]:
        """
        Validate a JWT access token.
        
        Checks:
        1. JWT signature validity
        2. Token expiration
        3. Token not in revocation list (Redis)
        
        Args:
            token: The JWT token string to validate
        
        Returns:
            AccessToken if valid, None if invalid or expired
        """
        try:
            # Check if token is revoked
            if await self.is_token_revoked(token):
                return None
            
            # Decode and verify JWT
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": True}
            )
            
            # Extract token information
            token_type_str = payload.get("token_type")
            token_type = TokenType.TWO_LEGGED if token_type_str == TokenType.TWO_LEGGED.value else TokenType.THREE_LEGGED
            
            expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            
            access_token = AccessToken(
                token=token,
                token_type=token_type,
                expires_at=expires_at,
                scopes=payload.get("scopes", []),
                client_id=payload.get("client_id"),
                user_id=payload.get("user_id"),
                device_info=payload.get("device")
            )
            
            return access_token
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a JWT access token by adding it to the Redis blacklist.
        
        Args:
            token: The token string to revoke
        
        Returns:
            True if token was revoked, False on error
        """
        try:
            # Decode to get expiration time
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}
            )
            
            exp = payload.get("exp")
            if not exp:
                return False
            
            # Calculate TTL until token would expire anyway
            now = datetime.now(timezone.utc)
            exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            ttl_seconds = int((exp_time - now).total_seconds())
            
            if ttl_seconds > 0:
                # Add to revocation list with TTL
                await self.redis_client.setex(
                    f"revoked_token:{token}",
                    ttl_seconds,
                    "1"
                )
                return True
            
            return False
            
        except Exception:
            return False
    
    async def is_token_revoked(self, token: str) -> bool:
        """
        Check if a token has been revoked.
        
        Args:
            token: The token string to check
        
        Returns:
            True if revoked, False otherwise
        """
        try:
            result = await self.redis_client.exists(f"revoked_token:{token}")
            # Redis returns an integer count of keys that exist
            return int(result) > 0
        except Exception:
            return False
    
    async def get_device_from_token(self, token: str) -> Optional[Device]:
        """
        Extract device information from a 3-legged token.
        
        Args:
            token: The token string
        
        Returns:
            Device info dict if available, None otherwise
        """
        access_token = await self.validate_token(token)
        
        if not access_token:
            return None
        
        if access_token.token_type != TokenType.THREE_LEGGED:
            return None
        
        return access_token.device_info
