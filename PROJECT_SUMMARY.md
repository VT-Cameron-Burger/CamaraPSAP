# CamaraPSAP - CAMARA API Implementation

A FastAPI-based implementation of CAMARA (Carrier API) standards for device identification and location services, with OAuth 2.0 authentication using JWT tokens and Redis.

## Features

### API Endpoints

**Device Identifier APIs** (`/device-identifier/vwip/`)
- `POST /retrieve-identifier` - Get device IMEI, TAC, manufacturer, model
- `POST /retrieve-type` - Get device type information
- `POST /retrieve-ppid` - Get pseudonymous platform-specific device identifier

**Location APIs** (`/location-retrieval/vwip/` and `/location-verification/vwip/`)
- `POST /retrieve` - Get device location (latitude/longitude, circle/polygon area)
- `POST /verify` - Verify if device is within a specified area

**OAuth 2.0 APIs** (`/oauth/`)
- `POST /token` - Obtain access tokens (client_credentials or authorization_code)
- `POST /revoke` - Revoke access tokens

### Authentication & Authorization

- **JWT Tokens**: Stateless token validation with embedded claims
- **Redis**: Token revocation blacklist with automatic expiration
- **2-Legged OAuth**: Client credentials flow for server-to-server
- **3-Legged OAuth**: Authorization code flow with user consent
- **Scope-Based Access Control**: Fine-grained permissions per endpoint

### Data Models

- **CAMARA-Compliant**: All models follow CAMARA common schema
- **Pydantic v2**: Modern type validation and serialization
- **Error Handling**: Standard CAMARA error codes (400, 401, 403, 404, 422, 429, 500-503)

### Database

- **PostgreSQL**: Production-ready relational database
- **SQLAlchemy 2.0**: Modern async-ready ORM
- **Read-Only Services**: Service layer performs lookups only (no writes)

## Quick Start

### 1. Prerequisites

- Python 3.10+ (tested with 3.10.19)
- PostgreSQL (via Docker)
- Redis (via Docker)

### 2. Setup

```bash
# Clone repository
cd /home/cameronburger/gra/CamaraPSAP

# Activate virtual environment
source ./.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and set your secrets (especially JWT_SECRET_KEY)
nano .env
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker compose up -d

# Initialize database (if needed)
python -c "from src.camarapsap.db.init_db import init_db; init_db()"
```

### 4. Run Server

```bash
# Development server with auto-reload
cd src
uvicorn camarapsap.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m camarapsap.main
```

### 5. Test Authentication

```bash
# Test JWT generation (no Redis required)
python test_jwt_simple.py

# Test full OAuth flow (requires server running)
python test_oauth_flow.py
```

## Project Structure

```
CamaraPSAP/
├── src/camarapsap/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Auth dependencies
│   ├── oauth.py                   # OAuth 2.0 token endpoint
│   ├── device_identifier.py       # Device API endpoints
│   ├── location_retrieval.py      # Location retrieval endpoint
│   ├── location_verification.py   # Location verification endpoint
│   ├── example_auth_integration.py # Auth integration example
│   ├── db/
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── init_db.py             # Database initialization
│   │   └── models/
│   │       ├── device.py          # Device model
│   │       └── location.py        # Location model
│   ├── models/
│   │   ├── common/                # CAMARA common models (13 files)
│   │   ├── device_identifier/     # Device identifier models
│   │   ├── location_retrieval/    # Location retrieval models
│   │   ├── location_verification/ # Location verification models
│   │   └── error_models/          # CAMARA error models
│   └── services/
│       ├── authorization.py       # JWT + Redis auth service
│       ├── identifier.py          # Device identifier service
│       └── location.py            # Location service
├── tests/
├── docker-compose.yml             # PostgreSQL + Redis
├── Dockerfile                     # Container image
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── AUTHORIZATION.md               # Auth system documentation
├── test_jwt_simple.py             # JWT test (standalone)
├── test_authorization.py          # Full auth test (needs Redis)
└── test_oauth_flow.py             # OAuth flow demo (needs server)
```

## Configuration

Environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql://camarapsap:password@localhost:5432/camarapsap

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Versions
DEVICE_VERSION_ID=vwip
LOCATION_VERSION_ID=vwip
```

## API Usage

### 1. Obtain Access Token

```bash
# 2-legged (client credentials)
curl -X POST http://localhost:8000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=my_client" \
  -d "client_secret=my_secret" \
  -d "scope=device-identifier:retrieve-identifier location-retrieval:read"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "device-identifier:retrieve-identifier location-retrieval:read"
}
```

### 2. Use Token in API Request

```bash
# Call device identifier API (when auth is enabled)
curl -X POST http://localhost:8000/device-identifier/vwip/retrieve-identifier \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "phoneNumber": "+1234567890"
    }
  }'
```

### 3. Revoke Token

```bash
curl -X POST http://localhost:8000/oauth/revoke \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d "client_id=my_client" \
  -d "client_secret=my_secret"
```

## Adding Authentication to Endpoints

To add authentication to your API endpoints:

1. Import dependencies:
```python
from camarapsap.dependencies import require_scope
from camarapsap.services.authorization import AccessToken, Scope
```

2. Add token parameter:
```python
@router.post("/my-endpoint")
async def my_endpoint(
    request: RequestBody,
    token: AccessToken = Depends(require_scope(Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER))
):
    # Token is validated, scope is checked
    # Access token info via: token.user_id, token.device_info, etc.
    pass
```

3. Update error responses:
```python
@router.post(
    "/my-endpoint",
    responses={
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
    }
)
```

See `example_auth_integration.py` for a complete example.

## Development

### Run Tests

```bash
# JWT generation and validation
python test_jwt_simple.py

# Full authorization service (requires Redis)
docker compose up -d redis
python test_authorization.py

# OAuth flow (requires server + Redis)
docker compose up -d
cd src && uvicorn camarapsap.main:app --reload &
python test_oauth_flow.py
```

### Database Operations

```bash
# Initialize database
python -c "from src.camarapsap.db.init_db import init_db; init_db()"

# Connect to PostgreSQL
docker compose exec postgres psql -U camarapsap
```

### Check Errors

```bash
# Type checking with mypy (if installed)
mypy src/camarapsap/

# Linting with ruff (if installed)
ruff check src/camarapsap/
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `device-identifier:retrieve-identifier` | Get device IMEI, TAC, manufacturer |
| `device-identifier:retrieve-type` | Get device type information |
| `device-identifier:retrieve-ppid` | Get pseudonymous device ID |
| `location-retrieval:read` | Retrieve device location |
| `location-verification:verify` | Verify device location |

## Security Considerations

### Production Checklist

- [ ] **Change JWT_SECRET_KEY** - Use strong random secret (never commit to git)
- [ ] **Enable HTTPS** - All API traffic must be encrypted
- [ ] **Validate Client Credentials** - Implement database validation in `oauth.py`
- [ ] **Add Rate Limiting** - Protect token endpoint from brute force
- [ ] **Enable Redis Auth** - Set Redis password in production
- [ ] **Implement Authorization Code Flow** - Add user consent UI
- [ ] **Add Refresh Tokens** - Implement token refresh mechanism
- [ ] **Log Security Events** - Track failed auth, revocations, anomalies
- [ ] **Consider RS256** - Use asymmetric keys for multi-service validation
- [ ] **Set CORS Properly** - Restrict allowed origins
- [ ] **Enable Redis Persistence** - Configure AOF/RDB for revocation list
- [ ] **Add Token Introspection** - Implement RFC 7662 endpoint

## Documentation

- **AUTHORIZATION.md** - Complete authorization system documentation
- **example_auth_integration.py** - Code examples for adding auth to endpoints
- **API Specs** - See YAML files for OpenAPI specifications

## Technologies

- **FastAPI** - Modern Python web framework
- **Pydantic v2** - Data validation and serialization
- **SQLAlchemy 2.0** - Database ORM
- **PostgreSQL** - Relational database
- **Redis** - Token revocation and caching
- **PyJWT** - JWT token generation and validation
- **Docker Compose** - Local development infrastructure

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions:
- Check AUTHORIZATION.md for auth-related questions
- Review example_auth_integration.py for implementation examples
- See CAMARA specifications: https://github.com/camaraproject

## API Versions

- Device Identifier: `vwip` (very work in progress)
- Location Services: `vwip` (very work in progress)

Versions can be configured in `.env` file.
