import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

import aio_pika
from aio_pika import ExchangeType
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.models.interaction import UserInteraction
from app.models.training import TrainingState
from app.schemas.events import RecommendationEvent
from app.services.cache import CacheService
from app.tasks.training import train_ials_model, update_user_profile


logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """Persistent RabbitMQ consumer for recommendation events from Django."""

    def __init__(self, settings: Settings, session_factory: async_sessionmaker[AsyncSession]):
        self.settings = settings
        self.session_factory = session_factory
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self.cache_service = CacheService(settings)

    async def connect(self) -> bool:
        try:
            self.connection = await aio_pika.connect_robust(
                self.settings.RABBITMQ_URL,
                heartbeat=600,
                timeout=30,
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=5)
            self.exchange = await self.channel.declare_exchange(
                name=self.settings.RABBITMQ_EXCHANGE,
                type=ExchangeType.TOPIC,
                durable=True,
            )
            self.queue = await self.channel.declare_queue(
                name=self.settings.RABBITMQ_QUEUE,
                durable=True,
            )
            await self.queue.bind(self.exchange, routing_key=self.settings.RABBITMQ_QUEUE)
            logger.info("RabbitMQ consumer initialized: %s -> %s", self.settings.RABBITMQ_EXCHANGE, self.settings.RABBITMQ_QUEUE)
            return True
        except Exception as exc:
            logger.error("Failed to connect to RabbitMQ: %s", exc, exc_info=True)
            return False

    async def consume(self):
        if not await self.connect():
            logger.error("Failed to start RabbitMQ consumer")
            return

        await self.queue.consume(self._on_message, no_ack=False)
        logger.info("RabbitMQ consumer started")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        except Exception as exc:
            logger.error("Consumer error: %s", exc, exc_info=True)
            await asyncio.sleep(5)
            await self.consume()

    async def _on_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        try:
            raw_data: Dict[str, Any] = json.loads(message.body.decode("utf-8"))
            if "excursion_id" not in raw_data and "item_id" in raw_data:
                raw_data["excursion_id"] = raw_data["item_id"]

            try:
                event = RecommendationEvent.model_validate(raw_data)
            except ValidationError as exc:
                logger.warning("Rejecting invalid recommendation event %s: %s", raw_data, exc)
                await message.reject(requeue=False)
                return

            async with message.process(requeue=False):
                event_data = event.model_dump()
                logger.info(
                    "Received event %s for excursion %s user %s",
                    event.event_type,
                    event.excursion_id,
                    event.user_id,
                )

                if event.event_type == "content_update":
                    train_ials_model.delay()
                    return

                if event.event_type != "popularity_update":
                    await self._save_interaction(event_data)

                if event.user_id:
                    await self.cache_service.invalidate_user_cache(event.user_id)
                    update_user_profile.delay(event.user_id)

                await self._update_training_state()
        except Exception as exc:
            logger.error(
                "Failed processing RabbitMQ message; rejecting without requeue: %s",
                exc,
                exc_info=True,
            )

    async def _save_interaction(self, event_data: Dict[str, Any]):
        async with self._get_db_session() as db:
            weight = event_data.get("weight")
            if weight is None:
                weight = self._get_event_weight(event_data.get("event_type"), event_data.get("duration_seconds"))

            db.add(
                UserInteraction(
                    user_id=event_data.get("user_id"),
                    session_id=event_data.get("session_id"),
                    excursion_id=event_data.get("excursion_id"),
                    event_type=event_data.get("event_type"),
                    weight=weight,
                    timestamp=self._parse_timestamp(event_data.get("timestamp")),
                )
            )
            await db.commit()

    async def _update_training_state(self):
        async with self._get_db_session() as db:
            state = await db.get(TrainingState, 1)
            if not state:
                state = TrainingState(id=1)
                db.add(state)

            state.total_interactions = (state.total_interactions or 0) + 1
            state.interactions_since_training = (state.interactions_since_training or 0) + 1
            retrain_threshold = state.retrain_threshold or 100
            if state.interactions_since_training >= retrain_threshold:
                train_ials_model.delay()
                state.interactions_since_training = 0
            state.retrain_threshold = retrain_threshold
            await db.commit()

    def _get_event_weight(self, event_type: str, duration: Optional[int] = None) -> float:
        weights = {
            "view": 0.3,
            "long_view": 0.7,
            "favorite": 0.8,
            "review": 0.9,
            "booking": 1.0,
        }
        return weights.get(event_type, 0.3)

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        if isinstance(timestamp, datetime):
            return timestamp
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return datetime.now(timezone.utc)
        return datetime.now(timezone.utc)

    @asynccontextmanager
    async def _get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()

    async def close(self):
        await self.cache_service.disconnect()
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
