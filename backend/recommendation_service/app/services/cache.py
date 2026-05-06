import json
import logging
from typing import List, Dict, Any, Optional
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client (will be initialized lazily)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get Redis client (lazy initialization)"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL)
    return _redis_client


async def get_cached_recommendations(cache_key: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached recommendations from Redis"""
    try:
        client = get_redis_client()
        cached_data = await client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting cached recommendations for {cache_key}: {e}")
        return None


async def set_cached_recommendations(
    cache_key: str,
    recommendations: List[Dict[str, Any]],
    ttl: int = 3600
) -> bool:
    """Cache recommendations in Redis"""
    try:
        client = get_redis_client()
        await client.setex(cache_key, ttl, json.dumps(recommendations))
        return True
        
    except Exception as e:
        logger.error(f"Error caching recommendations for {cache_key}: {e}")
        return False


async def invalidate_user_cache(user_id: int) -> bool:
    """Invalidate user recommendation cache"""
    try:
        client = get_redis_client()
        cache_key = f"user:{user_id}"
        await client.delete(cache_key)
        logger.info(f"Invalidated cache for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error invalidating cache for user {user_id}: {e}")
        return False


async def invalidate_similar_cache(excursion_id: int) -> bool:
    """Invalidate similar items cache"""
    try:
        client = get_redis_client()
        cache_key = f"similar:{excursion_id}"
        await client.delete(cache_key)
        logger.info(f"Invalidated similar cache for excursion {excursion_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error invalidating similar cache for excursion {excursion_id}: {e}")
        return False


async def clear_all_recommendation_cache() -> bool:
    """Clear all recommendation cache (for maintenance)"""
    try:
        client = get_redis_client()
        pattern = "user:*"
        keys = await client.keys(pattern)
        
        if keys:
            await client.delete(*keys)
            logger.info(f"Cleared {len(keys)} user recommendation caches")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clearing recommendation cache: {e}")
        return False


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    try:
        client = get_redis_client()
        info = await client.info()
        
        # Count recommendation cache keys
        user_keys = await client.keys("user:*")
        similar_keys = await client.keys("similar:*")
        
        return {
            "total_keys": info.get("db0", {}).get("keys", 0),
            "user_cache_keys": len(user_keys),
            "similar_cache_keys": len(similar_keys),
            "memory_usage": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0)
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {}
