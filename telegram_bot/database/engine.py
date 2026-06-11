from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models.base import Base
from core import settings

DATABASE_URL = settings.database_url

if not DATABASE_URL:
    raise ValueError("Database URL could not be constructed. Check your environment variables.")


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_session_depends() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
