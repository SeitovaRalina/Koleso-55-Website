from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    __absract__ = True
    metadata = MetaData()


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    try:
        # Test connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Create all tables
        from app.models.excursion import Excursion
        from app.models.user import UserInteraction, UserProfile
        from app.models.cache import RecommendationCache, SimilarCache
        from app.models.training import TrainingState
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection():
    """Check if database is connected"""
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
