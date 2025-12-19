"""Device identifier service layer."""

from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..db.models import Device
from ..db.models.device_ppid import DevicePPID as DevicePPIDModel
from ..models.device_identifier import DeviceIdentifier, DeviceType, DevicePPID
from ..models.common import Device as DeviceInput, DeviceResponse
from ..models.common.device_ipv4 import DeviceIpv4Addr


class DeviceIdentifierService:
    """Service for device identifier operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _create_device_response(self, device: Device, matched_by: str) -> DeviceResponse:
        """Create a DeviceResponse with only the matched identifier.
        
        Args:
            device: The database device object
            matched_by: The property that was used to match ('phoneNumber', 'networkAccessIdentifier', 'ipv4Address')
        
        Returns:
            DeviceResponse with only the matched identifier populated
        """
        if matched_by == "phoneNumber":
            return DeviceResponse(
                phoneNumber=device.phone_number,
                networkAccessIdentifier=None,
                ipv4Address=None,
                ipv6Address=None
            )
        elif matched_by == "networkAccessIdentifier":
            return DeviceResponse(
                phoneNumber=None,
                networkAccessIdentifier=device.network_access_identifier,
                ipv4Address=None,
                ipv6Address=None
            )
        elif matched_by == "ipv4Address":
            if device.ipv4_public_address:
                return DeviceResponse(
                    phoneNumber=None,
                    networkAccessIdentifier=None,
                    ipv4Address=DeviceIpv4Addr(
                        publicAddress=device.ipv4_public_address,
                        privateAddress=device.ipv4_private_address,
                        publicPort=device.ipv4_public_port
                    ),
                    ipv6Address=None
                )
        
        # Fallback - return None for all fields if no valid match
        return DeviceResponse(
            phoneNumber=None,
            networkAccessIdentifier=None,
            ipv4Address=None,
            ipv6Address=None
        )
    
    def get_device(self, device_input: DeviceInput) -> Tuple[Device, str]:
        """Get existing device based on input identifiers.
        
        Returns:
            Tuple of (Device, matched_property) where matched_property is the
            identifier that was successfully used to match the device
            (e.g., 'phoneNumber', 'networkAccessIdentifier', 'ipv4Address')
        
        Raises:
            HTTPException: 404 IDENTIFIER_NOT_FOUND if device is not found
        """
        # Try to find existing device by phone number
        if device_input.phone_number:
            device = self.db.query(Device).filter(
                Device.phone_number == device_input.phone_number
            ).first()
            if device:
                return device, "phoneNumber"
        
        # Try to find by network access identifier
        if device_input.network_access_identifier:
            device = self.db.query(Device).filter(
                Device.network_access_identifier == device_input.network_access_identifier
            ).first()
            if device:
                return device, "networkAccessIdentifier"
        
        # Try to find by IPv4 address
        if device_input.ipv4_address:
            device = self.db.query(Device).filter(
                Device.ipv4_public_address == device_input.ipv4_address.public_address
            ).first()
            if device:
                return device, "ipv4Address"
        
        # Device not found - raise 404 error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "IDENTIFIER_NOT_FOUND",
                "message": "Device identifier provided cannot be matched to a device"
            }
        )

    def retrieve_identifier(self, device_input: DeviceInput) -> DeviceIdentifier:
        """Retrieve device identifier information.
        
        Raises:
            HTTPException: 404 IDENTIFIER_NOT_FOUND if device is not found
        """
        device, matched_by = self.get_device(device_input)
        
        return DeviceIdentifier(
            lastChecked=device.last_checked,
            imei=device.imei,
            imeisv=device.imeisv,
            tac=device.tac,
            manufacturer=device.manufacturer,
            model=device.model,
            device=self._create_device_response(device, matched_by)
        )
    
    def retrieve_type(self, device_input: DeviceInput) -> DeviceType:
        """Retrieve device type information.
        
        Raises:
            HTTPException: 404 IDENTIFIER_NOT_FOUND if device is not found
        """
        device, matched_by = self.get_device(device_input)
        
        return DeviceType(
            lastChecked=device.last_checked,
            tac=device.tac,
            manufacturer=device.manufacturer,
            model=device.model,
            device=self._create_device_response(device, matched_by)
        )
    
    def retrieve_ppid(self, device_input: DeviceInput, client_id: str) -> DevicePPID:
        """Retrieve pseudonymous device identifier for a specific client.
        
        Args:
            device_input: Device identifiers to match
            client_id: The OAuth client ID requesting the PPID
        
        Raises:
            HTTPException: 404 IDENTIFIER_NOT_FOUND if device is not found
            HTTPException: 422 if device exists but ppid not set for this client
        """
        device, matched_by = self.get_device(device_input)
        
        # Query the device_ppid table for this device-client pair
        ppid_record = self.db.query(DevicePPIDModel).filter(
            DevicePPIDModel.device_id == device.id,
            DevicePPIDModel.client_id == client_id
        ).first()
        
        if not ppid_record:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "PPID_NOT_AVAILABLE",
                    "message": f"Pseudonymous device identifier is not available for this device and client"
                }
            )
        
        return DevicePPID(
            lastChecked=device.last_checked,
            ppid=ppid_record.ppid,
            device=self._create_device_response(device, matched_by)
        )
