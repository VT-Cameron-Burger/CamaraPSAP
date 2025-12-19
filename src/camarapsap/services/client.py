"""Client service for managing OAuth 2.0 clients."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
import secrets

from ..db.models.client import Client


class ClientService:
    """Service for managing OAuth 2.0 client applications."""
    
    @staticmethod
    def hash_secret(secret: str) -> str:
        """Hash a client secret using bcrypt."""
        # Convert to bytes and hash
        secret_bytes = secret.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(secret_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_secret(secret: str, hashed: str) -> bool:
        """Verify a client secret against its hash."""
        secret_bytes = secret.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(secret_bytes, hashed_bytes)
    
    @staticmethod
    def generate_client_secret(length: int = 24) -> str:
        """Generate a secure random client secret (max 24 chars for bcrypt)."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    async def create_client(
        session: AsyncSession,
        client_id: str,
        client_name: str,
        allowed_scopes: List[str],
        client_secret: Optional[str] = None
    ) -> tuple[Client, str]:
        """
        Create a new OAuth 2.0 client.
        
        Args:
            session: Database session
            client_id: Unique client identifier
            client_name: Human-readable client name
            allowed_scopes: List of scopes this client can request
            client_secret: Optional client secret (will be generated if not provided)
        
        Returns:
            Tuple of (Client object, plain-text client_secret)
        """
        if client_secret is None:
            client_secret = ClientService.generate_client_secret()
        
        client = Client(
            client_id=client_id,
            client_secret_hash=ClientService.hash_secret(client_secret),
            client_name=client_name,
            allowed_scopes=allowed_scopes,
            is_active=True
        )
        
        session.add(client)
        await session.commit()
        await session.refresh(client)
        
        return client, client_secret
    
    @staticmethod
    async def get_client(
        session: AsyncSession,
        client_id: str
    ) -> Optional[Client]:
        """
        Get a client by ID.
        
        Args:
            session: Database session
            client_id: Client identifier
        
        Returns:
            Client object if found, None otherwise
        """
        result = await session.execute(
            select(Client).where(Client.client_id == client_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_client(
        session: AsyncSession,
        client_id: str,
        client_secret: str
    ) -> Optional[Client]:
        """
        Authenticate a client using credentials.
        
        Args:
            session: Database session
            client_id: Client identifier
            client_secret: Client secret
        
        Returns:
            Client object if authenticated, None otherwise
        """
        client = await ClientService.get_client(session, client_id)
        
        if not client:
            return None
        
        if not client.is_active:
            return None
        
        if not ClientService.verify_secret(client_secret, client.client_secret_hash):
            return None
        
        return client
    
    @staticmethod
    async def validate_scopes(
        client: Client,
        requested_scopes: List[str]
    ) -> bool:
        """
        Check if requested scopes are allowed for the client.
        
        Args:
            client: Client object
            requested_scopes: List of requested scopes
        
        Returns:
            True if all scopes are allowed, False otherwise
        """
        return all(scope in client.allowed_scopes for scope in requested_scopes)
    
    @staticmethod
    async def deactivate_client(
        session: AsyncSession,
        client_id: str
    ) -> bool:
        """
        Deactivate a client (soft delete).
        
        Args:
            session: Database session
            client_id: Client identifier
        
        Returns:
            True if deactivated, False if not found
        """
        client = await ClientService.get_client(session, client_id)
        
        if not client:
            return False
        
        client.is_active = False
        await session.commit()
        return True
