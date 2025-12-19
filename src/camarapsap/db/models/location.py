"""Location database model."""

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .device import Device

from ..database import Base


class Location(Base):
    """Location table storing device location information."""
    
    __tablename__ = "locations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    
    # Location type and timestamp
    area_type: Mapped[str] = mapped_column(String(20))  # CIRCLE or POLYGON
    
    # Circle location data
    center_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    center_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Polygon location data (stored as JSON array of points)
    boundary: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="locations")
    
    def __repr__(self) -> str:
        return f"<Location(id={self.id}, device_id={self.device_id}, type={self.area_type})>"
