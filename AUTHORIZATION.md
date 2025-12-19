# Authorization System

This project implements OAuth 2.0 authorization with JWT tokens and Redis-based revocation tracking, following CAMARA security standards.

## Architecture

**JWT + Redis Hybrid Approach**

- **JWT Tokens**: Stateless token validation with embedded claims (user_id, scopes, device_info)
- **Redis**: Token revocation blacklist with automatic expiration
- **Benefit**: Fast validation without database queries, with ability to revoke tokens when needed

## Token Types

### 2-Legged Tokens (Client Credentials)

Used for server-to-server communication where the client provides device identifiers in each API request.

```python
from camarapsap.services.authorization import AuthorizationService, Scope

auth_service = AuthorizationService()

token = auth_service.create_two_legged_token(
    client_id="my_application",
    client_secret="secret_key_12345",
    scopes=[
        Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value,
        Scope.LOCATION_RETRIEVAL_READ.value
    ]
)

print(token.to_dict())
# {
#     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#     "token_type": "Bearer",
#     "expires_in": 3600,
#     "scope": "device-identifier:retrieve-identifier location-retrieval:read"
# }
```

### 3-Legged Tokens (Authorization Code)

Used when the end user has authenticated and consented. Token contains user and device information.

```python
token = auth_service.create_three_legged_token(
    client_id="my_application",
    authorization_code="auth_code_from_oauth_flow",
    scopes=[Scope.LOCATION_VERIFICATION_VERIFY.value],
    user_id="user_12345",
    device_info={
        "phoneNumber": "+1234567890",
        "ipv4Address": {"publicAddress": "192.0.2.1"}
    }
)
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `device-identifier:retrieve-identifier` | Retrieve device IMEI, TAC, manufacturer |
| `device-identifier:retrieve-type` | Retrieve device type information |
| `device-identifier:retrieve-ppid` | Retrieve pseudonymous device identifier |
| `location-retrieval:read` | Retrieve device location |
| `location-verification:verify` | Verify device location |

## Configuration

Set these environment variables (or use defaults in `config.py`):

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# JWT settings
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Using Authentication in Endpoints

### Add Authentication Dependency

```python
from fastapi import APIRouter, Depends
from camarapsap.dependencies import require_scope
from camarapsap.services.authorization import AccessToken, Scope

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(
    token: AccessToken = Depends(require_scope(Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER))
):
    # Token is automatically validated
    # Scope is verified
    # Access token information is available
    
    if token.token_type.value == "3-legged":
        # Use device info from token
        device_info = token.device_info
    else:
        # Require device in request body
        pass
    
    return {"message": "Authenticated!"}
```

### Optional Authentication

```python
from camarapsap.dependencies import get_current_token_optional

@router.get("/public-or-private")
async def flexible_endpoint(
    token: Optional[AccessToken] = Depends(get_current_token_optional)
):
    if token:
        # Authenticated request - provide enhanced features
        return {"user_id": token.user_id, "premium": True}
    else:
        # Public access - basic features
        return {"premium": False}
```

## Token Validation

The authorization service automatically validates:

1. **JWT Signature**: Verifies token authenticity
2. **Expiration**: Checks if token is still valid
3. **Revocation**: Queries Redis blacklist

```python
# Manual validation
access_token = auth_service.validate_token(token_string)

if access_token:
    print(f"Valid token for client: {access_token.client_id}")
    print(f"Scopes: {access_token.scopes}")
else:
    print("Invalid or expired token")
```

## Token Revocation

Revoke tokens to immediately invalidate them (e.g., on logout, security breach):

```python
# Revoke a token
revoked = auth_service.revoke_token(token_string)

if revoked:
    print("Token successfully revoked")
    
# Check if token is revoked
is_revoked = auth_service.is_token_revoked(token_string)
```

Revoked tokens are stored in Redis with TTL matching their original expiration time, so they automatically clean up when they would have expired anyway.

## API Usage Example

### 1. Obtain Token

```bash
# POST /oauth/token (implement this endpoint)
curl -X POST http://localhost:8000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=my_client" \
  -d "client_secret=my_secret" \
  -d "scope=device-identifier:retrieve-identifier"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "device-identifier:retrieve-identifier"
}
```

### 2. Use Token in API Request

```bash
curl -X POST http://localhost:8000/device-identifier/vwip/retrieve-identifier \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "phoneNumber": "+1234567890"
    }
  }'
```

## Testing

### Test JWT Generation (No Redis Required)

```bash
python test_jwt_simple.py
```

This tests:
- 2-legged token generation
- 3-legged token generation
- Token validation
- Expired token rejection
- Invalid token rejection

### Test Full Authorization Service (Requires Redis)

1. Start Redis:
```bash
docker compose up -d redis
```

2. Run full test:
```bash
python test_authorization.py
```

This tests:
- Token generation
- Token validation
- Token revocation
- Redis blacklist integration
- Device extraction from tokens

## Security Considerations

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong, random secret
- [ ] Use environment variables for secrets (never commit to git)
- [ ] Implement client credentials validation against database
- [ ] Add rate limiting on token endpoints
- [ ] Use HTTPS for all API communication
- [ ] Implement refresh token rotation
- [ ] Add logging for security events (failed auth, revocations)
- [ ] Consider using asymmetric keys (RS256) for multi-service validation
- [ ] Set up Redis password authentication
- [ ] Enable Redis persistence for revocation list durability

### JWT Claims

**2-Legged Token:**
```json
{
  "sub": "client_id",
  "client_id": "client_id",
  "token_type": "2-legged",
  "scopes": ["scope1", "scope2"],
  "iat": 1702761226,
  "exp": 1702764826,
  "iss": "camarapsap"
}
```

**3-Legged Token:**
```json
{
  "sub": "user_id",
  "client_id": "client_id",
  "token_type": "3-legged",
  "scopes": ["scope1"],
  "user_id": "user_id",
  "device": {
    "phoneNumber": "+1234567890",
    "ipv4Address": {"publicAddress": "192.0.2.1"}
  },
  "iat": 1702761226,
  "exp": 1702764826,
  "iss": "camarapsap"
}
```

## Error Responses

| Status | Error | Description |
|--------|-------|-------------|
| 401 | UNAUTHENTICATED | Missing or invalid token |
| 403 | PERMISSION_DENIED | Valid token but insufficient scopes |
| 429 | QUOTA_EXCEEDED | Rate limit exceeded |

Example error:
```json
{
  "status": 401,
  "code": "UNAUTHENTICATED",
  "message": "Invalid or expired access token"
}
```

## Integration with Existing Endpoints

To add authentication to existing endpoints:

1. Import dependencies:
```python
from camarapsap.dependencies import require_scope
from camarapsap.services.authorization import AccessToken, Scope
```

2. Add token parameter with scope requirement:
```python
async def my_endpoint(
    # ... other parameters ...
    token: AccessToken = Depends(require_scope(Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER))
):
```

3. Update error responses:
```python
@router.post(
    "/endpoint",
    responses={
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
        # ... other errors ...
    }
)
```

4. Handle token types in business logic:
```python
if token.token_type.value == "3-legged":
    device_info = token.device_info
else:
    if not request.device:
        raise HTTPException(400, "Device required for 2-legged tokens")
    device_info = request.device.model_dump()
```

See `example_auth_integration.py` for a complete example.
