"""Initialize the database and create tables."""

import asyncio
from .database import engine, Base
from .models.device import Device
from .models.location import Location
from .models.client import Client
from ..services.client import ClientService
from ..models.auth import Scope
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def init_db() -> None:
    """Create all database tables."""
    print("Creating database tables...")
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database tables created successfully")


async def seed_clients() -> None:
    """Seed database with test OAuth clients."""
    print("\nSeeding OAuth clients...")
    
    # Create async session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if clients already exist
        existing = await ClientService.get_client(session, "test_client_2legged")
        if existing:
            print("✓ Test clients already exist, skipping seed")
            return
        
        # Create 2-legged test client
        client_2leg, secret_2leg = await ClientService.create_client(
            session=session,
            client_id="test_client_2legged",
            client_name="Test Client (2-Legged)",
            allowed_scopes=[
                Scope.DEVICE_IDENTIFIER_RETRIEVE_IDENTIFIER.value,
                Scope.DEVICE_IDENTIFIER_RETRIEVE_TYPE.value,
                Scope.DEVICE_IDENTIFIER_RETRIEVE_PPID.value,
                Scope.LOCATION_RETRIEVAL_READ.value,
                Scope.LOCATION_VERIFICATION_VERIFY.value,
            ]
        )
        
        print(f"✓ Created 2-legged client:")
        print(f"  Client ID: {client_2leg.client_id}")
        print(f"  Client Secret: {secret_2leg}")
        print(f"  Allowed Scopes: {', '.join(client_2leg.allowed_scopes)}")
        
        # Create 3-legged test client
        client_3leg, secret_3leg = await ClientService.create_client(
            session=session,
            client_id="test_client_3legged",
            client_name="Test Client (3-Legged)",
            allowed_scopes=[
                Scope.LOCATION_VERIFICATION_VERIFY.value,
                Scope.LOCATION_RETRIEVAL_READ.value,
            ]
        )
        
        print(f"\n✓ Created 3-legged client:")
        print(f"  Client ID: {client_3leg.client_id}")
        print(f"  Client Secret: {secret_3leg}")
        print(f"  Allowed Scopes: {', '.join(client_3leg.allowed_scopes)}")
    
    print("\n✓ OAuth clients seeded successfully")
    print("\n" + "=" * 60)
    print("IMPORTANT: Save these credentials for testing!")
    print("=" * 60)


async def main() -> None:
    """Main initialization function."""
    try:
        await init_db()
        await seed_clients()
        
        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close engine
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
