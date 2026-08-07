from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from server.config import settings
from server.database.models import Base

# Engine configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with async_session_factory() as session:
        yield session

async def init_db() -> None:
    """Create tables (useful for development)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
