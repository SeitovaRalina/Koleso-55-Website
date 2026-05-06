from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db, check_db_connection
from app.core.config import settings
from app.models.training import TrainingState
from app.schemas.health import HealthResponse
import aio_pika
import redis.asyncio as redis

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    
    # Check database connection
    db_connected = await check_db_connection()
    
    # Check RabbitMQ connection
    rabbitmq_connected = False
    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, timeout=5)
        await connection.close()
        rabbitmq_connected = True
    except Exception:
        pass
    
    # Check Redis connection
    redis_connected = False
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        redis_connected = True
    except Exception:
        pass
    
    # Check if models are ready
    models_ready = False
    try:
        result = await db.execute(select(TrainingState).limit(1))
        training_state = result.scalar_one_or_none()
        models_ready = training_state.models_ready if training_state else False
    except Exception:
        pass
    
    return HealthResponse(
        status="ok" if all([db_connected, rabbitmq_connected, redis_connected]) else "degraded",
        models_ready=models_ready,
        db_connected=db_connected,
        rabbitmq_connected=rabbitmq_connected,
        redis_connected=redis_connected
    )
