import logging
from typing import Dict, List, Any

import httpx
from tenacity import after_log, before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.core.config import Settings


logger = logging.getLogger(__name__)


class DjangoClient:
    """Async client for Django API communication"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.DJANGO_BASE_URL.rstrip('/')
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(15.0, connect=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.ERROR),
    )
    async def fetch_excursions(self) -> List[Dict[str, Any]]:
        """Fetch all excursions from Django API"""
        try:
            response = await self.client.get(
                "/api/analytics/internal/excursions/",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            excursions = response.json()
            logger.info(f"Fetched {len(excursions)} excursions from Django API")
            return excursions
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching excursions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching excursions: {e}")
            raise

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.ERROR),
    )
    async def fetch_popularity(self) -> Dict[int, int]:
        """Fetch popularity data from Django API"""
        try:
            response = await self.client.get(
                "/api/analytics/internal/popularity/",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            popularity = response.json()
            logger.info(f"Fetched popularity data for {len(popularity)} excursions")
            return {int(k): int(v) for k, v in popularity.items()}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching popularity: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching popularity: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("Django client closed")
