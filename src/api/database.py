"""Database configuration and session management

Sets up SQLAlchemy async engine and session factory for PostgreSQL.
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Get database URL from environment variable
# Default uses 'postgres' hostname for Docker Compose service name
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://simlab:simlab_dev@postgres:5432/sdlc_simlab"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions

    Usage in FastAPI endpoints:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables

    Creates all tables defined by models.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
