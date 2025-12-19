"""Simple test script for JWT token generation (no Redis required)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta, timezone
import jwt
from camarapsap.config import settings
from camarapsap.services.authorization import Scope, TokenType


def create_simple_jwt(payload: dict, expires_in_minutes: int = 60) -> str:
    """Create a JWT token without using the full service."""
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


def validate_simple_jwt(token: str) -> dict:
    """Validate a JWT token."""
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"verify_exp": True}
    )


def main():
    """Test JWT token generation and validation."""
    
    print("=" * 60)
    print("Testing JWT Token Generation (No Redis)")
    print("=" * 60)
    
    # Test 2-legged token
    print("\n1. Creating 2-legged JWT token (client credentials)...")
    two_legged_payload = {
        "sub": "test_client_123",
        "client_id": "test_client_123",
        "token_type": TokenType.TWO_LEGGED.value,
        "scopes": [
            Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value,
            Scope.LOCATION_RETRIEVAL_READ.value
        ],
    }
    
    two_legged_token = create_simple_jwt(two_legged_payload)
    print(f"   Token created (length: {len(two_legged_token)} chars)")
    print(f"   Token (first 80 chars): {two_legged_token[:80]}...")
    
    # Decode and display
    decoded = validate_simple_jwt(two_legged_token)
    print(f"\n   Decoded payload:")
    print(f"   - Subject: {decoded['sub']}")
    print(f"   - Client ID: {decoded['client_id']}")
    print(f"   - Token Type: {decoded['token_type']}")
    print(f"   - Scopes: {', '.join(decoded['scopes'])}")
    print(f"   - Issued At: {datetime.fromtimestamp(decoded['iat'], tz=timezone.utc)}")
    print(f"   - Expires At: {datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)}")
    print(f"   - Issuer: {decoded['iss']}")
    
    # Test 3-legged token
    print("\n2. Creating 3-legged JWT token (authorization code)...")
    device_info = {
        "phoneNumber": "+1234567890",
        "ipv4Address": {"publicAddress": "192.0.2.1"}
    }
    
    three_legged_payload = {
        "sub": "user_789",
        "client_id": "test_client_456",
        "token_type": TokenType.THREE_LEGGED.value,
        "scopes": [Scope.LOCATION_VERIFICATION_VERIFY.value],
        "user_id": "user_789",
        "device": device_info
    }
    
    three_legged_token = create_simple_jwt(three_legged_payload)
    print(f"   Token created (length: {len(three_legged_token)} chars)")
    print(f"   Token (first 80 chars): {three_legged_token[:80]}...")
    
    # Decode and display
    decoded = validate_simple_jwt(three_legged_token)
    print(f"\n   Decoded payload:")
    print(f"   - Subject: {decoded['sub']}")
    print(f"   - Client ID: {decoded['client_id']}")
    print(f"   - Token Type: {decoded['token_type']}")
    print(f"   - User ID: {decoded['user_id']}")
    print(f"   - Scopes: {', '.join(decoded['scopes'])}")
    print(f"   - Device Info: {decoded['device']}")
    print(f"   - Expires At: {datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)}")
    
    # Test invalid token
    print("\n3. Testing invalid token validation...")
    try:
        invalid_token = "invalid.jwt.token"
        validate_simple_jwt(invalid_token)
        print(f"   ✗ Invalid token was accepted (should fail)")
    except jwt.InvalidTokenError:
        print(f"   ✓ Invalid token rejected as expected")
    
    # Test expired token
    print("\n4. Testing expired token validation...")
    expired_payload = {
        "sub": "test_client",
        "client_id": "test_client",
        "token_type": TokenType.TWO_LEGGED.value,
        "scopes": [Scope.LOCATION_RETRIEVAL_READ.value],
    }
    expired_token = create_simple_jwt(expired_payload, expires_in_minutes=-1)
    
    try:
        validate_simple_jwt(expired_token)
        print(f"   ✗ Expired token was accepted (should fail)")
    except jwt.ExpiredSignatureError:
        print(f"   ✓ Expired token rejected as expected")
    
    # Configuration info
    print("\n5. JWT Configuration:")
    print(f"   - Algorithm: {settings.jwt_algorithm}")
    print(f"   - Access Token Expiry: {settings.jwt_access_token_expire_minutes} minutes")
    print(f"   - Refresh Token Expiry: {settings.jwt_refresh_token_expire_days} days")
    
    print("\n" + "=" * 60)
    print("JWT tests completed successfully!")
    print("=" * 60)
    print("\nNote: To test full authorization service with Redis revocation,")
    print("start the Redis service with: docker compose up -d redis")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
