"""Test script for authorization service."""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camarapsap.services.authorization import AuthorizationService
from camarapsap.models.auth import Scope, TokenType


async def main() -> None:
    """Test authorization service with JWT tokens."""
    
    print("=" * 60)
    print("Testing Authorization Service with JWT + Redis")
    print("=" * 60)
    
    # Initialize authorization service
    auth_service = AuthorizationService()
    
    # Test 2-legged token
    print("\n1. Creating 2-legged token (client credentials)...")
    two_legged_token = auth_service.create_two_legged_token(
        client_id="test_client_123",
        client_secret="test_secret",
        scopes=[
            Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value,
            Scope.LOCATION_RETRIEVAL_READ.value
        ]
    )
    
    print(f"   Token Type: {two_legged_token.token_type}")
    print(f"   Client ID: {two_legged_token.client_id}")
    print(f"   Scopes: {', '.join(two_legged_token.scopes)}")
    print(f"   Expires At: {two_legged_token.expires_at}")
    print(f"   Token (first 50 chars): {two_legged_token.token[:50]}...")
    
    # Test 3-legged token
    print("\n2. Creating 3-legged token (authorization code)...")
    device_info = {
        "phoneNumber": "+1234567890",
        "ipv4Address": {"publicAddress": "192.0.2.1"}
    }
    
    three_legged_token = auth_service.create_three_legged_token(
        client_id="test_client_456",
        authorization_code="auth_code_xyz",
        scopes=[
            Scope.LOCATION_VERIFICATION_VERIFY.value
        ],
        user_id="user_789",
        device_info=device_info
    )
    
    print(f"   Token Type: {three_legged_token.token_type}")
    print(f"   Client ID: {three_legged_token.client_id}")
    print(f"   User ID: {three_legged_token.user_id}")
    print(f"   Scopes: {', '.join(three_legged_token.scopes)}")
    print(f"   Device Info: {three_legged_token.device_info}")
    print(f"   Token (first 50 chars): {three_legged_token.token[:50]}...")
    
    # Validate tokens
    print("\n3. Validating 2-legged token...")
    validated = await auth_service.validate_token(two_legged_token.token)
    if validated:
        print(f"   ✓ Token is valid")
        print(f"   ✓ Has location-retrieval:read scope: {validated.has_scope(Scope.LOCATION_RETRIEVAL_READ.value)}")
    else:
        print(f"   ✗ Token validation failed")
    
    print("\n4. Validating 3-legged token...")
    validated = await auth_service.validate_token(three_legged_token.token)
    if validated:
        print(f"   ✓ Token is valid")
        device = await auth_service.get_device_from_token(three_legged_token.token)
        print(f"   ✓ Device info extracted: {device}")
    else:
        print(f"   ✗ Token validation failed")
    
    # Test revocation
    print("\n5. Revoking 2-legged token...")
    revoked = await auth_service.revoke_token(two_legged_token.token)
    if revoked:
        print(f"   ✓ Token revoked successfully")
    else:
        print(f"   ✗ Token revocation failed")
    
    print("\n6. Validating revoked token...")
    validated = await auth_service.validate_token(two_legged_token.token)
    if validated:
        print(f"   ✗ Token is still valid (should be revoked)")
    else:
        print(f"   ✓ Token validation failed as expected (revoked)")
    
    # Test API response format
    print("\n7. Token response format for API:")
    print(f"   {three_legged_token.to_dict()}")
    
    print("\n" + "=" * 60)
    print("Authorization tests completed successfully!")
    print("=" * 60)
    
    # Close Redis connection
    await auth_service.redis_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
