"""Location service layer."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from ..db.models import Device, Location as LocationModel
from ..models.location_retrieval import Location, Circle, RetrievalLocationRequest
from ..models.location_verification import VerifyLocationRequest, VerifyLocationResponse, VerificationResult
from ..models.common import Point, Device as DeviceInput


class LocationService:
    """Service for location operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_device(self, device_input: Optional[DeviceInput]) -> Optional[Device]:
        """Get existing device based on input identifiers."""
        if not device_input:
            return None
        
        # Try to find existing device by phone number
        if device_input.phone_number:
            device = self.db.query(Device).filter(
                Device.phone_number == device_input.phone_number
            ).first()
            if device:
                return device
        
        # Try to find by network access identifier
        if device_input.network_access_identifier:
            device = self.db.query(Device).filter(
                Device.network_access_identifier == device_input.network_access_identifier
            ).first()
            if device:
                return device
        
        # Try to find by IPv4 address
        if device_input.ipv4_address:
            device = self.db.query(Device).filter(
                Device.ipv4_public_address == device_input.ipv4_address.public_address
            ).first()
            if device:
                return device
        
        return None
    def retrieve_location(self, request: RetrievalLocationRequest) -> Location:
        """Retrieve device location."""
        # In a real implementation, query network for actual location
        # For now, return placeholder circular area
        center = Point(latitude=50.735851, longitude=7.10066)
        radius = 800
        
        return Location(
            lastLocationTime=datetime.now(timezone.utc),
            area=Circle(
                areaType="CIRCLE",
                center=center,
                radius=radius
            ),
            device=None
        )
    
    def verify_location(self, request: VerifyLocationRequest) -> VerifyLocationResponse:
        """Verify if device is within specified area."""
        # In a real implementation, compare network location with requested area
        # For now, return placeholder TRUE result
        
        return VerifyLocationResponse(
            verificationResult=VerificationResult.TRUE,
            lastLocationTime=datetime.now(timezone.utc),
            matchRate=None,
            device=None
        )
