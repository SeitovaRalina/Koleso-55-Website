from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from app.core.config import Settings, get_settings

from contextlib import contextmanager

# Global sync engine singleton
_sync_engine: Engine | None = None
_sync_sessionmaker: sessionmaker[Session] | None = None


def create_sync_engine(settings: Settings) -> Engine:
    """Get cached synchronous database engine singleton"""
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    engine = create_engine(
        sync_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    return engine


def create_sync_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=Session,
        autoflush=False,
    )

def get_sync_engine() -> Engine:
    """Get or create cached synchronous engine (singleton)"""
    global _sync_engine, _sync_sessionmaker

    if _sync_engine is None:
        settings = get_settings()
        _sync_engine = create_sync_engine(settings)
        _sync_sessionmaker = create_sync_sessionmaker(_sync_engine)

    return _sync_engine


def get_sync_sessionmaker() -> sessionmaker[Session]:
    """Get or create cached sessionmaker"""
    get_sync_engine()
    return _sync_sessionmaker


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """Context manager style: get synchronous session.
    
    Usage:
        with get_sync_db() as db:
            ...
    """
    session_factory = get_sync_sessionmaker()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_sync_db_session() -> Session:
    """Get session manually (caller must close it!)"""
    session_factory = get_sync_sessionmaker()
    return session_factory()
