from django.conf import settings
from django.utils import timezone
import requests

from .tasks import publish_event


EVENT_WEIGHTS = {
    "view": 0.3,
    "long_view": 0.7,
    "favorite": 0.8,
    "review": 0.9,
    "booking": 1.0,
}


def publish_recommendation_event(
    *,
    event_type: str,
    excursion_id: int,
    user_id: int | None = None,
    session_id: str | None = None,
    source: str | None = None,
    duration_seconds: int | None = None,
) -> None:
    event_data = {
        "event_type": event_type,
        "user_id": user_id,
        "session_id": session_id,
        "excursion_id": excursion_id,
        "weight": EVENT_WEIGHTS.get(event_type),
        "timestamp": timezone.now().replace(tzinfo=None).isoformat(),
        "source": source,
        "duration_seconds": duration_seconds,
    }
    publish_event.delay(event_data)


def _recommender_base_url() -> str:
    return getattr(settings, "RECOMMENDER_BASE_URL", "http://recommender_api:8000").rstrip("/")


def get_user_recommendations(user_id: int, top_k: int = 20) -> list[dict]:
    try:
        response = requests.get(
            f"{_recommender_base_url()}/api/v1/recommendations/user/{user_id}",
            params={"top_k": top_k, "exclude_interacted": "true"},
            timeout=2,
        )
        response.raise_for_status()
        return response.json().get("recommendations", [])
    except requests.RequestException:
        return []


def get_similar_excursions(excursion_id: int, top_k: int = 10) -> list[dict]:
    try:
        response = requests.get(
            f"{_recommender_base_url()}/api/v1/similar/{excursion_id}",
            params={"top_k": top_k},
            timeout=2,
        )
        response.raise_for_status()
        return response.json().get("similar_excursions", [])
    except requests.RequestException:
        return []
