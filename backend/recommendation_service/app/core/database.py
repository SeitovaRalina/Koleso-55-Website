from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create database engine"""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Enable SQL logging for debugging
        pool_pre_ping=True,
        pool_recycle=300,
    )


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session factory"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session
