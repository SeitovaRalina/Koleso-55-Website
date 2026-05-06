from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@postgres:5432/recommender"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    RABBITMQ_QUEUE: str = "excursion_events"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    
    # Model configuration
    MODEL_PATH: str = "/app/models/"
    TOP_K: int = 20
    HYBRID_ALPHA: float = 0.35
    POPULARITY_WEIGHT: float = 0.2
    COLD_START_MIN_INTERACTIONS: int = 3
    
    # IALS parameters
    IALS_FACTORS: int = 128
    IALS_REGULARIZATION: float = 0.05
    IALS_ITERATIONS: int = 15
    IALS_ALPHA: float = 2.0
    
    # PostgreSQL pgvector
    PGVECTOR_INDEX_LISTS: int = 100
    
    # Training
    RETRAIN_THRESHOLD: int = 100
    
    class Config:
        env_file = ".env"


settings = Settings()
