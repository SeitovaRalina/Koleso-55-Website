from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database - Recommendation service specific
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/recommender",
        description="PostgreSQL database URL for recommendation service"
    )

    # RabbitMQ
    RABBITMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="RabbitMQ connection URL"
    )
    RABBITMQ_QUEUE: str = Field(
        default="excursion_events",
        description="RabbitMQ queue name"
    )
    RABBITMQ_EXCHANGE: str = Field(
        default="excursion_events",
        description="RabbitMQ exchange name"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend"
    )
    
    # Django API
    DJANGO_BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Django API base URL"
    )
    
    # Model paths
    MODEL_PATH: str = Field(
        default="/app/models/",
        description="Path to model files"
    )
    
    # Recommendation settings
    TOP_K: int = Field(
        default=20,
        description="Number of recommendations to return"
    )
    COLD_START_MIN_INTERACTIONS: int = Field(
        default=3,
        description="Minimum interactions for cold start"
    )
    HYBRID_ALPHA: float = Field(
        default=0.35,
        description="Weight for content-based recommendations"
    )
    POPULARITY_WEIGHT: float = Field(
        default=0.2,
        description="Weight for popularity in hybrid recommendations"
    )
    
    # iALS settings
    IALS_FACTORS: int = Field(
        default=128,
        description="Number of latent factors for iALS"
    )
    IALS_REGULARIZATION: float = Field(
        default=0.05,
        description="Regularization parameter for iALS"
    )
    IALS_ITERATIONS: int = Field(
        default=15,
        description="Number of iterations for iALS"
    )
    IALS_ALPHA: float = Field(
        default=2.0,
        description="Alpha parameter for iALS"
    )
    
    # pgvector
    PGVECTOR_INDEX_LISTS: int = Field(
        default=100,
        description="Number of index lists for pgvector"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()
