"""Client application model for OAuth 2.0."""

from typing import List
from sqlalchemy import String, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .device_ppid import DevicePPID

from ..database import Base


class Client(Base):
    """OAuth 2.0 client application."""
    
    __tablename__ = "clients"
    
    client_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    client_secret_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_scopes: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    device_ppids: Mapped[List["DevicePPID"]] = relationship("DevicePPID", back_populates="client", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<Client(client_id='{self.client_id}', name='{self.client_name}')>"
