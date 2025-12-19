"""
Complete OAuth 2.0 flow demonstration.

This script demonstrates:
1. Starting the FastAPI server
2. Obtaining access tokens via OAuth endpoint
3. Using tokens to make authenticated API requests
4. Revoking tokens

Note: Requires Redis to be running for full functionality.
"""

import sys
import time
import requests
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_response(response: requests.Response):
    """Print response details."""
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")


def get_2_legged_token() -> Dict[str, Any]:
    """Obtain a 2-legged access token (client credentials flow)."""
    print_section("1. Obtaining 2-Legged Token (Client Credentials)")
    
    response = requests.post(
        f"{API_BASE_URL}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client_123",
            "client_secret": "test_secret_456",
            "scope": "device-identifier:retrieve-identifier location-retrieval:read"
        }
    )
    
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to obtain token: {response.text}")


def get_3_legged_token() -> Dict[str, Any]:
    """Obtain a 3-legged access token (authorization code flow)."""
    print_section("2. Obtaining 3-Legged Token (Authorization Code)")
    
    response = requests.post(
        f"{API_BASE_URL}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": "test_client_789",
            "client_secret": "test_secret_789",
            "code": "auth_code_xyz",
            "scope": "location-verification:verify",
            "user_id": "user_123",
            "device_phone": "+1234567890"
        }
    )
    
    print_response(response)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to obtain token: {response.text}")


def use_token_success(token_data: Dict[str, Any]):
    """Make an authenticated API request with valid token."""
    print_section("3. Using Token for API Request (Should Succeed)")
    
    access_token = token_data["access_token"]
    
    # Note: This will fail if the endpoint doesn't have authentication enabled
    # This is just an example of how to use the token
    print("\nExample request (endpoint needs authentication enabled):")
    print(f"Authorization: Bearer {access_token[:50]}...")
    print("(See example_auth_integration.py for how to add auth to endpoints)")


def use_token_wrong_scope():
    """Try to use a token without the required scope."""
    print_section("4. Using Token Without Required Scope (Should Fail)")
    
    # Get token with limited scope
    response = requests.post(
        f"{API_BASE_URL}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "location-retrieval:read"  # Wrong scope for device identifier
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token obtained with scope: {token_data['scope']}")
        print("\nAttempting to access device-identifier endpoint...")
        print("(Would return 403 Forbidden if endpoint checks scopes)")


def revoke_token(token_data: Dict[str, Any]):
    """Revoke an access token."""
    print_section("5. Revoking Token")
    
    access_token = token_data["access_token"]
    
    response = requests.post(
        f"{API_BASE_URL}/oauth/revoke",
        data={
            "token": access_token,
            "client_id": "test_client_123",
            "client_secret": "test_secret_456"
        }
    )
    
    print_response(response)


def use_revoked_token(token_data: Dict[str, Any]):
    """Try to use a revoked token."""
    print_section("6. Using Revoked Token (Should Fail)")
    
    print("(Would return 401 Unauthorized if endpoint checks token)")


def main():
    """Run the complete OAuth flow demonstration."""
    
    print("=" * 60)
    print("OAuth 2.0 Flow Demonstration")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. FastAPI server running: python -m camarapsap.main")
    print("   or: uvicorn camarapsap.main:app --reload")
    print("2. Redis running: docker compose up -d redis")
    print("   (for token revocation)")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ Server health check failed")
            print("  Start server: cd src && uvicorn camarapsap.main:app --reload")
            return
    except requests.exceptions.RequestException:
        print("\n✗ Cannot connect to API server")
        print("  Start server: cd src && uvicorn camarapsap.main:app --reload")
        return
    
    print("\n✓ Server is running\n")
    
    try:
        # Get 2-legged token
        token_2_legged = get_2_legged_token()
        time.sleep(1)
        
        # Get 3-legged token
        token_3_legged = get_3_legged_token()
        time.sleep(1)
        
        # Use token successfully
        use_token_success(token_2_legged)
        time.sleep(1)
        
        # Try wrong scope
        use_token_wrong_scope()
        time.sleep(1)
        
        # Revoke token
        revoke_token(token_2_legged)
        time.sleep(1)
        
        # Try to use revoked token
        use_revoked_token(token_2_legged)
        
        print("\n" + "=" * 60)
        print("Demonstration Complete!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Add authentication to endpoints (see example_auth_integration.py)")
        print("2. Implement client credential validation in oauth.py")
        print("3. Add authorization code flow with user consent")
        print("4. Set up proper JWT secret in production")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
