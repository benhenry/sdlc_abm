"""FastAPI dependencies

Provides dependency injection for database sessions and other shared resources.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency

    Usage in route functions:
        async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async for session in get_db():
        yield session
