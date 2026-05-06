from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
import logging
import numpy as np
from datetime import datetime

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.user import UserProfile, UserInteraction
from app.models.excursion import Excursion
from app.services.cache import invalidate_user_cache

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
def update_user_profile(self, user_id: int):
    """Update user profile based on their interactions"""
    import asyncio
    
    async def _update_profile():
        try:
            # Get user interactions
            result = await self.db.execute(
                select(UserInteraction)
                .where(UserInteraction.user_id == user_id)
                .order_by(UserInteraction.timestamp.desc())
            )
            interactions = result.scalars().all()
            
            if not interactions:
                logger.warning(f"No interactions found for user {user_id}")
                return {"status": "no_interactions", "user_id": user_id}
            
            # Get or create user profile
            result = await self.db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                profile = UserProfile(user_id=user_id)
                self.db.add(profile)
            
            # Update content vector (weighted average of excursion embeddings)
            await _update_content_vector(profile, interactions, self.db)
            
            # Update interaction count
            profile.interaction_count = len(interactions)
            profile.last_updated = datetime.utcnow()
            
            await self.db.commit()
            
            # Invalidate cache
            await invalidate_user_cache(user_id)
            
            logger.info(f"Updated profile for user {user_id}")
            return {
                "status": "completed",
                "user_id": user_id,
                "interaction_count": profile.interaction_count
            }
            
        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {e}")
            await self.db.rollback()
            raise
    
    return asyncio.run(_update_profile())


async def _update_content_vector(profile: UserProfile, interactions, db: AsyncSession):
    """Update user's content vector based on their interactions"""
    
    # Get weighted excursion embeddings
    excursion_ids = [inter.excursion_id for inter in interactions]
    weights = [inter.weight for inter in interactions]
    
    if not excursion_ids:
        return
    
    # Query excursions with embeddings
    result = await db.execute(
        select(Excursion.excursion_id, Excursion.embedding)
        .where(
            Excursion.excursion_id.in_(excursion_ids),
            Excursion.has_embedding == True,
            Excursion.embedding.isnot(None)
        )
    )
    excursion_data = result.all()
    
    if not excursion_data:
        logger.warning(f"No embeddings found for user's interacted excursions")
        return
    
    # Create mapping from excursion_id to embedding
    embedding_map = {row.excursion_id: row.embedding for row in excursion_data}
    
    # Calculate weighted average
    weighted_embeddings = []
    total_weight = 0
    
    for excursion_id, weight in zip(excursion_ids, weights):
        if excursion_id in embedding_map:
            embedding = np.array(embedding_map[excursion_id])
            weighted_embeddings.append(embedding * weight)
            total_weight += weight
    
    if weighted_embeddings:
        content_vector = np.sum(weighted_embeddings, axis=0) / total_weight
        profile.content_vector = content_vector.tolist()
    
    # IALS factors will be updated during model training
    # For now, we leave them as they are
