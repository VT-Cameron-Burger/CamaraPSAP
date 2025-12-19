"""Device database model."""

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .location import Location
    from .device_ppid import DevicePPID

from ..database import Base


class Device(Base):
    """Device table storing device information."""
    
    __tablename__ = "devices"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Device identifiers
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    network_access_identifier: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    ipv4_public_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    ipv4_private_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    ipv4_public_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ipv6_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Device details
    imei: Mapped[str] = mapped_column(String(15), nullable=False)
    imeisv: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_checked: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="device", cascade="all, delete-orphan", lazy="select")
    ppids: Mapped[List["DevicePPID"]] = relationship("DevicePPID", back_populates="device", cascade="all, delete-orphan", lazy="select")
    
    @property
    def tac(self) -> str:
        """Type Allocation Code - first 8 digits of IMEI."""
        return self.imei[:8]
    
    def __repr__(self) -> str:
        return f"<Device(id={self.id}, phone={self.phone_number}, imei={self.imei})>"
