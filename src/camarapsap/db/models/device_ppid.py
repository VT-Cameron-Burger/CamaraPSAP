"""Device PPID (Pseudonymous Portable Identifier) model."""

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .device import Device
    from .client import Client

from ..database import Base


class DevicePPID(Base):
    """Pseudonymous Portable Identifier for a device-client pair.
    
    Each PPID is unique to a specific device and client combination,
    allowing the client to reference the device without exposing
    sensitive identifiers like phone numbers or IMEI.
    """
    
    __tablename__ = "device_ppids"
    
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        primary_key=True
    )
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.client_id", ondelete="CASCADE"),
        primary_key=True
    )
    ppid: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="ppids")
    client: Mapped["Client"] = relationship("Client", back_populates="device_ppids")
    
    def __repr__(self) -> str:
        return f"<DevicePPID(device_id={self.device_id}, client_id={self.client_id}, ppid={self.ppid})>"
