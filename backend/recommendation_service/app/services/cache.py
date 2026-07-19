import json
import logging
from typing import Optional, List, Dict, Any

import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.core.config import Settings
from app.models.cache import RecommendationCache, SimilarCache

logger = logging.getLogger(__name__)


class CacheService:
    """Unified Redis cache service for recommendations"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._redis: Optional[Redis] = None

    async def connect(self) -> Redis:
        """Lazy connection to Redis"""
        if self._redis is None:
            self._redis = redis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Connected to Redis")
        return self._redis

    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis connection closed")

    async def get_user_recommendations(self, user_id: int) -> Optional[List[Dict]]:
        """Get cached recommendations for user"""
        try:
            redis_client = await self.connect()
            key = f"rec:user:{user_id}"
            data = await redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting user recommendations cache: {e}")
            return None

    async def set_user_recommendations(
        self, 
        user_id: int, 
        recommendations: List[Dict],
        ttl: int = 3600  # 1 hour
    ):
        """Cache user recommendations"""
        try:
            redis_client = await self.connect()
            key = f"rec:user:{user_id}"
            await redis_client.setex(key, ttl, json.dumps(recommendations))
            logger.debug(f"Cached recommendations for user {user_id}")
        except Exception as e:
            logger.error(f"Error caching user recommendations: {e}")

    async def get_similar_excursions(self, excursion_id: int) -> Optional[List[Dict]]:
        """Get cached similar excursions"""
        try:
            redis_client = await self.connect()
            key = f"sim:{excursion_id}"
            data = await redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting similar excursions cache: {e}")
            return None

    async def set_similar_excursions(
        self,
        excursion_id: int,
        similar_excursions: List[Dict],
        ttl: int = 86400  # 24 hours
    ):
        """Cache similar excursions"""
        try:
            redis_client = await self.connect()
            key = f"sim:{excursion_id}"
            await redis_client.setex(key, ttl, json.dumps(similar_excursions))
            logger.debug(f"Cached similar excursions for {excursion_id}")
        except Exception as e:
            logger.error(f"Error caching similar excursions: {e}")

    async def invalidate_user_cache(self, user_id: int):
        """Invalidate all caches for a specific user"""
        try:
            redis_client = await self.connect()
            await redis_client.delete(f"rec:user:{user_id}")
            logger.info(f"Invalidated cache for user {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")

    async def invalidate_all_user_caches(self):
        """Invalidate all user recommendation caches (after retraining)"""
        try:
            redis_client = await self.connect()
            # Используем scan для больших объемов
            async for key in redis_client.scan_iter(match="rec:user:*"):
                await redis_client.delete(key)
            logger.info("Invalidated all user recommendation caches")
        except Exception as e:
            logger.error(f"Error invalidating all user caches: {e}")

    async def invalidate_similar_cache(self, excursion_id: int):
        """Invalidate similar excursions cache"""
        try:
            redis_client = await self.connect()
            await redis_client.delete(f"sim:{excursion_id}")
        except Exception as e:
            logger.error(f"Error invalidating similar cache: {e}")

    async def save_recommendation_cache_db(
        self,
        db: AsyncSession,
        user_id: int,
        recommendations: List[Dict],
    ) -> None:
        """Persist a compact recommendation snapshot in Postgres."""
        excursion_ids = [item["excursion_id"] for item in recommendations]
        scores = [float(item.get("score", 0.0)) for item in recommendations]
        stmt = insert(RecommendationCache).values(
            user_id=user_id,
            excursion_ids=excursion_ids,
            scores=scores,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[RecommendationCache.user_id],
            set_={
                "excursion_ids": excursion_ids,
                "scores": scores,
            },
        )
        await db.execute(stmt)

    async def save_similar_cache_db(
        self,
        db: AsyncSession,
        excursion_id: int,
        similar_excursions: List[Dict],
    ) -> None:
        """Persist a compact similar-items snapshot in Postgres."""
        similar_ids = [item["excursion_id"] for item in similar_excursions]
        scores = [float(item.get("score", item.get("similarity", 0.0))) for item in similar_excursions]
        stmt = insert(SimilarCache).values(
            excursion_id=excursion_id,
            similar_ids=similar_ids,
            scores=scores,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[SimilarCache.excursion_id],
            set_={
                "similar_ids": similar_ids,
                "scores": scores,
            },
        )
        await db.execute(stmt)
