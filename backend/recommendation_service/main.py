import asyncio
import aio_pika
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.logging import setup_logging, RequestLoggingMiddleware
from app.routers import recommendations, similar, admin
from app.services.consumer import RabbitMQConsumer

from app.core.database import create_engine, create_sessionmaker
from app.services.cache import CacheService
from app.services.django_client import DjangoClient

from app.models.training import TrainingState


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    settings = get_settings()

    engine = create_engine(settings)
    session_factory = create_sessionmaker(engine)

    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.settings = settings

    cache_service = CacheService(settings)
    await cache_service.connect()
    app.state.cache_service = cache_service

    consumer = RabbitMQConsumer(settings, session_factory)
    consumer_task = asyncio.create_task(consumer.consume())
    app.state.consumer = consumer
    app.state.consumer_task = consumer_task

    django_client = DjangoClient(settings)
    app.state.django_client = django_client

    yield

    consumer_task.cancel()
    await consumer.close()
    await cache_service.disconnect()
    await engine.dispose()
    await django_client.close()


def create_app() -> FastAPI:
    """Create FastAPI application"""
    setup_logging()

    app = FastAPI(
        title="Recommendation Microservice",
        description="Microservice for excursion recommendations",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
    app.include_router(similar.router, prefix="/api/v1/similar", tags=["similar"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

    @app.get("/health", tags=["health"])
    async def health_check():
        settings = get_settings()

        db_connected = False
        rabbitmq_connected = False
        models_ready = False

        try:
            async with app.state.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_connected = True
        except:
            db_connected = False

        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            await connection.close()
            rabbitmq_connected = True
        except:
            rabbitmq_connected = False

        try:
            async with app.state.session_factory() as session:
                result = await session.execute(select(TrainingState))
                state = result.scalar_one_or_none()
                models_ready = state.models_ready if state else False
        except:
            models_ready = False

        return {
            "status": "healthy" if db_connected and rabbitmq_connected else "unhealthy",
            "db_connected": db_connected,
            "rabbitmq_connected": rabbitmq_connected,
            "models_ready": models_ready
        }
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
