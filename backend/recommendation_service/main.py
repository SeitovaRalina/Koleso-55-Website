from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.database import init_db
from app.core.rabbitmq import rabbitmq_consumer
from backend.recommendation_service.app.api.api import api_router
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting recommendation service...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Start RabbitMQ consumer in background
    consumer_task = asyncio.create_task(rabbitmq_consumer())
    logger.info("RabbitMQ consumer started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down recommendation service...")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    logger.info("Shutdown complete")


app = FastAPI(
    title="Recommendation Service",
    description="Personalized recommendations for travel excursions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "recommendation-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
