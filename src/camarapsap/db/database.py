"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..config import settings

# Database URL - using PostgreSQL with async driver
DATABASE_URL = getattr(settings, 'database_url', 'postgresql://camarapsap:camarapsap@localhost:5432/camarapsap')
# Convert to async URL
ASYNC_DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True  # Set to False in production
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Base class for models
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db():
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        yield session
