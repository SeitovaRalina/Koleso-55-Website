import logging
from typing import Dict, List, Optional, Union

import numpy as np
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.excursions import Excursion
from app.models.interaction import UserInteraction
from app.models.profile import UserProfile
from app.services.cache import CacheService
from app.services.collaborative import CollaborativeService
from app.services.django_client import DjangoClient


logger = logging.getLogger(__name__)


class HybridService:
    """Hybrid recommendations: content + collaborative factors + popularity."""

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        settings: Settings,
        collaborative_service: Optional[CollaborativeService],
        cache_service: CacheService,
        django_client: DjangoClient,
    ):
        self.db = db
        self.settings = settings
        self.collaborative_service = collaborative_service
        self.cache_service = cache_service
        self.django_client = django_client
        self.is_async = isinstance(db, AsyncSession)

    async def _execute(self, stmt):
        return await self.db.execute(stmt) if self.is_async else self.db.execute(stmt)

    async def _commit(self):
        if self.is_async:
            await self.db.commit()
        else:
            self.db.commit()

    async def _get_max_popularity(self) -> int:
        result = await self._execute(select(func.max(Excursion.popularity)))
        return int(result.scalar() or 1)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    async def score(self, user_id: int, excursion_id: int) -> Dict[str, float]:
        content_score = 0.0
        collab_score = 0.0
        popularity_score = 0.0

        try:
            profile = await self.db.get(UserProfile, user_id) if self.is_async else self.db.get(UserProfile, user_id)
            result = await self._execute(select(Excursion).where(Excursion.excursion_id == excursion_id))
            excursion = result.scalar_one_or_none()
            if not excursion:
                return {"content_score": 0.0, "collab_score": 0.0, "popularity_score": 0.0, "final_score": 0.0}

            if profile and profile.content_vector is not None and excursion.embedding is not None:
                content_score = self._cosine_similarity(
                    np.array(profile.content_vector),
                    np.array(excursion.embedding),
                )

            if profile and profile.ials_factors is not None and excursion.ials_factors is not None:
                raw_collab = float(np.dot(np.array(profile.ials_factors), np.array(excursion.ials_factors)))
                collab_score = 1 / (1 + np.exp(-raw_collab))
            elif self.collaborative_service:
                collab_score = await self.collaborative_service.predict(user_id, excursion_id)

            max_popularity = await self._get_max_popularity()
            popularity_score = min(1.0, float(excursion.popularity or 0) / max_popularity)

            final_score = (
                self.settings.HYBRID_ALPHA * content_score
                + (1 - self.settings.HYBRID_ALPHA - self.settings.POPULARITY_WEIGHT) * collab_score
                + self.settings.POPULARITY_WEIGHT * popularity_score
            )
            final_score = max(0.0, min(1.0, final_score))
            return {
                "content_score": round(content_score, 4),
                "collab_score": round(collab_score, 4),
                "popularity_score": round(popularity_score, 4),
                "final_score": round(final_score, 4),
            }
        except Exception as exc:
            logger.error("Error calculating score for user %s, excursion %s: %s", user_id, excursion_id, exc, exc_info=True)
            return {"content_score": 0.0, "collab_score": 0.0, "popularity_score": 0.0, "final_score": 0.0}

    async def get_user_recommendations(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        limit: int = 20,
        exclude_interacted: bool = True,
    ) -> List[dict]:
        if not user_id:
            return await self._get_popular_recommendations(limit)

        cached = await self.cache_service.get_user_recommendations(user_id)
        if cached:
            return cached[:limit]

        interaction_count = await self._get_user_interaction_count(user_id)
        if interaction_count < self.settings.COLD_START_MIN_INTERACTIONS:
            recommendations = await self._get_popular_recommendations(limit)
        else:
            recommendations = await self._generate_hybrid_recommendations(user_id, limit, exclude_interacted)

        if recommendations:
            await self.cache_service.set_user_recommendations(user_id, recommendations)
            if self.is_async:
                await self.cache_service.save_recommendation_cache_db(self.db, user_id, recommendations)
                await self._commit()

        return recommendations[:limit]

    async def _generate_hybrid_recommendations(
        self,
        user_id: int,
        limit: int,
        exclude_interacted: bool,
    ) -> List[dict]:
        result = await self._execute(
            select(Excursion.excursion_id, Excursion.title, Excursion.category, Excursion.price)
            .where(Excursion.has_embedding == True)
            .where(Excursion.embedding.is_not(None))
        )
        excursions = result.all()
        if not excursions:
            return []

        interacted = set()
        if exclude_interacted:
            int_result = await self._execute(
                select(UserInteraction.excursion_id).where(UserInteraction.user_id == user_id)
            )
            interacted = {row[0] for row in int_result.all()}

        scored_items = []
        for excursion in excursions:
            if excursion.excursion_id in interacted:
                continue
            score_data = await self.score(user_id, excursion.excursion_id)
            scored_items.append(
                {
                    "excursion_id": excursion.excursion_id,
                    "score": score_data["final_score"],
                    "title": excursion.title,
                    "category": excursion.category,
                    "price": float(excursion.price),
                    **score_data,
                }
            )

        scored_items.sort(key=lambda item: item["score"], reverse=True)
        return scored_items[:limit]

    async def _get_user_interaction_count(self, user_id: int) -> int:
        result = await self._execute(
            select(func.count(UserInteraction.id)).where(UserInteraction.user_id == user_id)
        )
        return int(result.scalar() or 0)

    async def _get_popular_recommendations(self, limit: int) -> List[dict]:
        result = await self._execute(
            select(Excursion)
            .order_by(desc(Excursion.popularity), desc(Excursion.review_count), Excursion.excursion_id)
            .limit(limit)
        )
        excursions = result.scalars().all()
        max_popularity = max([exc.popularity or 0 for exc in excursions] or [1])
        if max_popularity == 0:
            max_popularity = 1

        return [
            {
                "excursion_id": excursion.excursion_id,
                "score": round((excursion.popularity or 0) / max_popularity, 4),
                "title": excursion.title,
                "category": excursion.category,
                "price": float(excursion.price),
                "content_score": 0.0,
                "collab_score": 0.0,
                "popularity_score": round((excursion.popularity or 0) / max_popularity, 4),
            }
            for excursion in excursions
        ]
