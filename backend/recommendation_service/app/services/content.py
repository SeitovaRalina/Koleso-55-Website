import asyncio
import logging
from typing import List, Union

import numpy as np
import torch
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from transformers import AutoModel, AutoTokenizer

from app.models.excursions import Excursion
from app.models.interaction import UserInteraction
from app.models.profile import UserProfile
from app.services.cache import CacheService


logger = logging.getLogger(__name__)


class ContentService:
    """Content-based recommendation service with RuBERT embeddings."""

    def __init__(self, db: Union[AsyncSession, Session], settings, cache_service: CacheService):
        self.db = db
        self.settings = settings
        self.cache_service = cache_service
        self._model = None
        self._tokenizer = None
        self._model_lock = asyncio.Lock()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_async = isinstance(db, AsyncSession)

    async def _load_model(self):
        async with self._model_lock:
            if self._model is None or self._tokenizer is None:
                model_name = "DeepPavlov/rubert-base-cased"
                logger.info("Loading RuBERT model %s", model_name)
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._model = AutoModel.from_pretrained(model_name)
                self._model.to(self.device)
                self._model.eval()

    async def _execute(self, stmt):
        return await self.db.execute(stmt) if self.is_async else self.db.execute(stmt)

    async def _commit(self):
        if self.is_async:
            await self.db.commit()
        else:
            self.db.commit()

    async def _rollback(self):
        if self.is_async:
            await self.db.rollback()
        else:
            self.db.rollback()

    def _get(self, model, pk):
        return self.db.get(model, pk)

    async def compute_embedding(self, text: str) -> List[float]:
        await self._load_model()
        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)

        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * mask_expanded, 1)
        sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
        return (sum_embeddings / sum_mask).cpu().numpy()[0].tolist()

    async def update_excursion_embedding(self, excursion_id: int) -> bool:
        try:
            result = await self._execute(select(Excursion).where(Excursion.excursion_id == excursion_id))
            excursion = result.scalar_one_or_none()
            if not excursion:
                logger.warning("Excursion %s not found", excursion_id)
                return False

            text_for_embedding = f"{excursion.title} {excursion.description} {excursion.category}"
            if excursion.has_embedding and excursion.text_for_embedding == text_for_embedding:
                return True

            excursion.embedding = await self.compute_embedding(text_for_embedding)
            excursion.has_embedding = True
            excursion.last_updated = func.now()
            excursion.text_for_embedding = text_for_embedding
            await self._commit()
            await self.cache_service.invalidate_similar_cache(excursion_id)
            return True
        except Exception as exc:
            logger.error("Error updating excursion embedding %s: %s", excursion_id, exc, exc_info=True)
            await self._rollback()
            return False

    async def compute_user_profile(self, user_id: int) -> List[float]:
        try:
            result = await self._execute(
                select(UserInteraction.weight, Excursion.embedding)
                .join(Excursion, UserInteraction.excursion_id == Excursion.excursion_id)
                .where(UserInteraction.user_id == user_id)
                .where(Excursion.has_embedding == True)
                .where(Excursion.embedding.is_not(None))
                .order_by(UserInteraction.timestamp.desc())
            )
            interactions = result.all()
            if not interactions:
                logger.info("No interactions with embeddings found for user %s", user_id)
                return []

            weights = np.array([float(row[0]) for row in interactions])
            embeddings = np.array([row[1] for row in interactions])
            content_vector = np.average(embeddings, axis=0, weights=weights).tolist()

            user_profile = await self.db.get(UserProfile, user_id) if self.is_async else self.db.get(UserProfile, user_id)
            if user_profile:
                user_profile.content_vector = content_vector
                user_profile.interaction_count = len(interactions)
                user_profile.last_updated = func.now()
            else:
                self.db.add(
                    UserProfile(
                        user_id=user_id,
                        content_vector=content_vector,
                        interaction_count=len(interactions),
                        last_updated=func.now(),
                    )
                )

            await self._commit()
            return content_vector
        except Exception as exc:
            logger.error("Error computing user profile %s: %s", user_id, exc, exc_info=True)
            await self._rollback()
            return []

    async def get_similar_excursions(self, excursion_id: int, limit: int = 10) -> List[dict]:
        cached = await self.cache_service.get_similar_excursions(excursion_id)
        if cached:
            return cached[:limit]

        try:
            result = await self._execute(
                select(Excursion)
                .where(Excursion.excursion_id == excursion_id)
                .where(Excursion.has_embedding == True)
                .where(Excursion.embedding.is_not(None))
            )
            target = result.scalar_one_or_none()
            if not target or target.embedding is None:
                return []

            distance_expr = Excursion.embedding.cosine_distance(target.embedding)
            result = await self._execute(
                select(
                    Excursion.excursion_id,
                    Excursion.title,
                    Excursion.category,
                    Excursion.price,
                    (1 - distance_expr).label("similarity_score"),
                )
                .where(Excursion.excursion_id != excursion_id)
                .where(Excursion.has_embedding == True)
                .where(Excursion.embedding.is_not(None))
                .order_by(distance_expr)
                .limit(limit)
            )

            similar_list = [
                {
                    "excursion_id": row.excursion_id,
                    "score": max(0.0, min(1.0, float(row.similarity_score))),
                    "title": row.title,
                    "category": row.category,
                    "price": float(row.price),
                }
                for row in result.all()
            ]

            if similar_list:
                await self.cache_service.set_similar_excursions(excursion_id, similar_list)
                if self.is_async:
                    await self.cache_service.save_similar_cache_db(self.db, excursion_id, similar_list)
                    await self.db.commit()

            return similar_list
        except Exception as exc:
            logger.error("Error getting similar excursions for %s: %s", excursion_id, exc, exc_info=True)
            return []
