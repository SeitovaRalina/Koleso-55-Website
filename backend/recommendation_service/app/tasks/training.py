import asyncio
import logging
from datetime import datetime

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.sync_database import get_sync_db
from app.models.excursions import Excursion
from app.models.interaction import UserInteraction
from app.models.profile import UserProfile
from app.services.cache import CacheService
from app.services.collaborative import CollaborativeService
from app.services.content import ContentService
from app.services.django_client import DjangoClient
from app.services.hybrid import HybridService
from app.tasks.celery_app import celery_app


logger = logging.getLogger(__name__)
settings = get_settings()


def run_async(coro):
    return asyncio.run(coro)


async def _fetch_django_data():
    client = DjangoClient(settings)
    try:
        excursions = await client.fetch_excursions()
        popularity = await client.fetch_popularity()
        return excursions, popularity
    finally:
        await client.close()


def _text_for_embedding(excursion_data: dict) -> str:
    return " ".join(
        str(excursion_data.get(field) or "")
        for field in ("title", "description", "category")
    ).strip()


def _upsert_excursions(db, excursions: list[dict], popularity: dict[int, int]) -> list[int]:
    changed_or_missing_ids: list[int] = []

    for item in excursions:
        excursion_id = int(item["id"])
        text_for_embedding = _text_for_embedding(item)
        existing = db.execute(
            select(Excursion).where(Excursion.excursion_id == excursion_id)
        ).scalar_one_or_none()

        values = {
            "excursion_id": excursion_id,
            "title": item.get("title") or "",
            "description": item.get("description") or item.get("short_description") or "",
            "category": item.get("category") or "",
            "location_type": item.get("location_type") or "",
            "price": float(item.get("price") or 0),
            "duration": int(item.get("duration") or 0),
            "average_rating": item.get("average_rating"),
            "review_count": int(item.get("review_count") or 0),
            "popularity": int(popularity.get(excursion_id, 0)),
            "text_for_embedding": text_for_embedding,
            "last_updated": func.now(),
        }

        if existing:
            if existing.text_for_embedding != text_for_embedding or not existing.has_embedding:
                changed_or_missing_ids.append(excursion_id)
            for field, value in values.items():
                setattr(existing, field, value)
        else:
            db.add(Excursion(**values))
            changed_or_missing_ids.append(excursion_id)

    db.commit()
    return changed_or_missing_ids


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30, name="app.tasks.training.update_user_profile")
def update_user_profile(self, user_id: int):
    try:
        with get_sync_db() as db:
            cache_service = CacheService(settings)
            content_service = ContentService(db, settings, cache_service)
            result = run_async(content_service.compute_user_profile(user_id))
            run_async(cache_service.invalidate_user_cache(user_id))
            return {"status": "success" if result else "no_data", "user_id": user_id}
    except Exception as exc:
        logger.error("update_user_profile failed for %s: %s", user_id, exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60, name="app.tasks.training.train_ials_model")
def train_ials_model(self):
    """Full pipeline: sync Django data, compute embeddings, train iALS, rebuild caches."""
    try:
        excursions, popularity = run_async(_fetch_django_data())

        with get_sync_db() as db:
            changed_ids = _upsert_excursions(db, excursions, popularity)
            cache_service = CacheService(settings)
            content_service = ContentService(db, settings, cache_service)

            for excursion_id in changed_ids:
                run_async(content_service.update_excursion_embedding(excursion_id))

            collab_service = CollaborativeService(db, settings, cache_service)
            trained = run_async(collab_service.train())

        rebuild_all_caches.delay()
        return {
            "status": "success",
            "excursions_synced": len(excursions),
            "embeddings_updated": len(changed_ids),
            "ials_trained": trained,
        }
    except Exception as exc:
        logger.error("train_ials_model failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.training.rebuild_all_caches")
def rebuild_all_caches():
    try:
        with get_sync_db() as db:
            cache_service = CacheService(settings)
            django_client = DjangoClient(settings)
            content_service = ContentService(db, settings, cache_service)
            hybrid_service = HybridService(
                db=db,
                settings=settings,
                collaborative_service=None,
                cache_service=cache_service,
                django_client=django_client,
            )

            run_async(cache_service.invalidate_all_user_caches())

            excursion_ids = db.execute(
                select(Excursion.excursion_id)
                .where(Excursion.has_embedding == True)
                .where(Excursion.embedding.is_not(None))
            ).scalars().all()
            for excursion_id in excursion_ids[:500]:
                run_async(content_service.get_similar_excursions(excursion_id, limit=10))

            active_users = db.execute(
                select(UserInteraction.user_id)
                .where(UserInteraction.user_id.is_not(None))
                .distinct()
                .limit(1000)
            ).scalars().all()
            for user_id in active_users:
                run_async(hybrid_service.get_user_recommendations(user_id=user_id, limit=settings.TOP_K))

            run_async(django_client.close())

        return {
            "status": "success",
            "processed_users": len(active_users),
            "processed_excursions": len(excursion_ids),
        }
    except Exception as exc:
        logger.error("rebuild_all_caches failed: %s", exc, exc_info=True)
        return {"status": "failed", "error": str(exc)}


@celery_app.task(name="app.tasks.training.check_data_integrity")
def check_data_integrity():
    try:
        with get_sync_db() as db:
            missing_embeddings = db.execute(
                select(func.count(Excursion.id)).where(Excursion.has_embedding == False)
            ).scalar() or 0
            active_users = db.execute(
                select(UserInteraction.user_id)
                .where(UserInteraction.user_id.is_not(None))
                .distinct()
            ).scalars().all()
            users_without_profile = [
                user_id
                for user_id in active_users
                if not db.get(UserProfile, user_id) or not db.get(UserProfile, user_id).content_vector
            ]

        return {
            "excursions_without_embedding": int(missing_embeddings),
            "active_users": len(active_users),
            "users_without_profile": len(users_without_profile),
            "status": "warning" if missing_embeddings or users_without_profile else "healthy",
            "checked_at": datetime.utcnow().isoformat(),
        }
    except Exception as exc:
        logger.error("check_data_integrity failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
