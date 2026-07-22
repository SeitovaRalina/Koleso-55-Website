import ssl
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    """Create database engine"""
    connect_args = {}
    if settings.DB_SSLMODE in {'require', 'verify-ca', 'verify-full'}:
        if settings.DB_SSLROOTCERT:
            ssl_context = ssl.create_default_context(cafile=settings.DB_SSLROOTCERT)
        else:
            ssl_context = ssl.create_default_context()

        if settings.DB_SSLMODE == 'require':
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        elif settings.DB_SSLMODE == 'verify-ca':
            ssl_context.check_hostname = False

        connect_args['ssl'] = ssl_context

    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args,
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
