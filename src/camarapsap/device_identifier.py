"""Device Identifier API endpoints."""

from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional, Annotated
from datetime import datetime
from sqlalchemy.orm import Session
from .config import settings
from .models.auth import AccessToken
from .models.common.device import Device
from .models.device_identifier import (
    RequestBody,
    DeviceIdentifier,
    DeviceType,
    DevicePPID,
)
from .models.error_models.camara_errors import (
    Error400,
    Error401,
    Error403,
    Error404,
    Error422,
    Error429,
)
from .services.identifier import DeviceIdentifierService
from .db.database import get_db
from .dependencies import get_current_token

router = APIRouter(
    prefix=f"/device-identifier/{settings.device_version_id}",
    tags=["Get Device Identifiers"]
)

# Reusable dependency annotations
CurrentToken = Annotated[AccessToken, Depends(get_current_token)]
DatabaseSession = Annotated[Session, Depends(get_db)]

def get_identifier_service(db: DatabaseSession) -> DeviceIdentifierService:
    """Create a DeviceIdentifierService instance."""
    return DeviceIdentifierService(db)

IdentifierService = Annotated[DeviceIdentifierService, Depends(get_identifier_service)]

def _validate_device_xor_token(request: RequestBody, token: AccessToken) -> Device:
    if request.device and token.device_info:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "UNNECESSARY_IDENTIFIER",
                "message": "Device identifier cannot be provided when token contains device info"
            }
        )
    device = request.device or token.device_info
    if not device:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "MISSING_IDENTIFIER",
                "message": "Device identifier must be provided"
            }
        )
    return device

@router.post(
    "/retrieve-identifier",
    responses={
        400: {"model": Error400, "description": "Bad Request"},
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
        404: {"model": Error404, "description": "Not Found"},
        422: {"model": Error422, "description": "Unprocessable Content"},
        429: {"model": Error429, "description": "Too Many Requests"},
    }
)
async def retrieve_identifier(
    request: RequestBody,
    token: CurrentToken,
    service: IdentifierService,
    x_correlator: Optional[str] = Header(None, alias="x-correlator")
) -> DeviceIdentifier:
    """
    Get details about the specific device being used by a given mobile subscriber.
    
    Returns device IMEI, IMEISV, TAC, manufacturer and model information.
    
    Args:
        version_id: API version identifier
        request: Request body with optional device identification
        x_correlator: Correlation id for the different services
        
    Returns:
        Device identifier details including IMEI/IMEISV
    """
    device = _validate_device_xor_token(request, token)
    
    return service.retrieve_identifier(device)


@router.post(
    "/retrieve-type",
    responses={
        400: {"model": Error400, "description": "Bad Request"},
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
        404: {"model": Error404, "description": "Not Found"},
        422: {"model": Error422, "description": "Unprocessable Content"},
        429: {"model": Error429, "description": "Too Many Requests"},
    }
)
async def retrieve_type(
    request: RequestBody,
    token: CurrentToken,
    service: IdentifierService,
    x_correlator: Optional[str] = Header(None, alias="x-correlator")
) -> DeviceType:
    """
    Get details about the type of device being used by a given mobile subscriber.
    
    Returns device TAC, manufacturer and model information only.
    
    Args:
        version_id: API version identifier
        request: Request body with optional device identification
        x_correlator: Correlation id for the different services
        
    Returns:
        Device type details (TAC, manufacturer, model)
    """
    device = _validate_device_xor_token(request, token)

    return service.retrieve_type(device)


@router.post(
    "/retrieve-ppid",
    responses={
        400: {"model": Error400, "description": "Bad Request"},
        401: {"model": Error401, "description": "Unauthorized"},
        403: {"model": Error403, "description": "Forbidden"},
        404: {"model": Error404, "description": "Not Found"},
        422: {"model": Error422, "description": "Unprocessable Content"},
        429: {"model": Error429, "description": "Too Many Requests"},
    },
    summary="Retrieve PPID"
)
async def retrieve_ppid(
    request: RequestBody,
    token: CurrentToken,
    service: IdentifierService,
    x_correlator: Optional[str] = Header(None, alias="x-correlator")
) -> DevicePPID:
    """
    Retrieve PPID.
    
    Get a pseudonymous identifier for device being used by a given mobile subscriber.
    
    Returns a pairwise pseudonymous identifier unique to but persistent for the API consumer.
    
    Args:
        version_id: API version identifier
        request: Request body with optional device identification
        x_correlator: Correlation id for the different services
        
    Returns:
        Pseudonymous device identifier (PPID)
    """
    
    # Extract client_id from the validated token
    client_id = token.client_id
    if not client_id:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "UNAUTHENTICATED",
                "message": "Client ID not found in token"
            }
        )
    device = _validate_device_xor_token(request, token)
    
    return service.retrieve_ppid(device, client_id)
