from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import logging
from datetime import datetime, timedelta

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.cache import RecommendationCache, SimilarCache

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    
    def __init__(self):
        self._db = None

    @property
    def db(self) -> AsyncSession:
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Clean up database session after task completion"""
        if self._db:
            import asyncio
            asyncio.create_task(self._db.close())
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def cleanup_old_cache(self):
    """Clean up old cache entries"""
    import asyncio
    
    async def _cleanup():
        try:
            # Clean up recommendation cache older than 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Delete old recommendation cache
            result = await self.db.execute(
                delete(RecommendationCache)
                .where(RecommendationCache.created_at < cutoff_time)
            )
            rec_deleted = result.rowcount
            
            # Delete old similar cache (keep for 48 hours)
            cutoff_time_similar = datetime.utcnow() - timedelta(hours=48)
            result = await self.db.execute(
                delete(SimilarCache)
                .where(SimilarCache.created_at < cutoff_time_similar)
            )
            sim_deleted = result.rowcount
            
            await self.db.commit()
            
            logger.info(f"Cache cleanup completed: {rec_deleted} recommendation entries, {sim_deleted} similar entries")
            
            return {
                "status": "completed",
                "recommendation_cache_deleted": rec_deleted,
                "similar_cache_deleted": sim_deleted
            }
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            await self.db.rollback()
            raise
    
    return asyncio.run(_cleanup())
