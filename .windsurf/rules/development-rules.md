---
trigger: always_on
---

# PROJECT CONTEXT
Implement a recommendation microservice for a travel excursion booking platform. The main backend is Django REST Framework with RabbitMQ as message broker. Develop in sequential stages, each producing a working result.

# TECHNOLOGY STACK
- FastAPI (Python 3.12+) with async routes
- PostgreSQL with pgvector extension
- RabbitMQ (aio-pika for async consumer)
- Redis (redis-py with async support)
- Celery (for training tasks)
- SQLAlchemy 2.0 (async, with Mapped, mapped_column, declarative base)
- Alembic (async migrations, run_async in env.py)
- Docker & docker-compose
- HuggingFace Transformers (DeepPavlov/rubert-base-cased)
- implicit library (AlternatingLeastSquares)
- pydantic-settings (BaseSettings for config)
- httpx (async client for Django API calls)

# PROJECT STRUCTURE
recommender/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py (Settings class with BaseSettings, reads from .env)
│   │   ├── database.py (async engine, async_sessionmaker, get_db dependency)
│   │   ├── di.py (Depends functions for all services)
│   │   └── exceptions.py
│   ├── models/
│   │   ├── base.py (declarative Base)
│   │   ├── excursion.py
│   │   ├── interaction.py
│   │   ├── profile.py
│   │   ├── cache.py (RecommendationCache, SimilarCache)
│   │   └── training.py (TrainingState)
│   ├── schemas/ (pydantic v2 models for request/response)
│   ├── services/
│   │   ├── content.py (ContentService class)
│   │   ├── collaborative.py (CollaborativeService class)
│   │   ├── hybrid.py (HybridService class)
│   │   ├── cache.py (CacheService class)
│   │   ├── consumer.py (RabbitMQConsumer class)
│   │   └── django_client.py (DjangoClient class)
│   ├── routers/
│   │   ├── recommendations.py
│   │   ├── similar.py
│   │   └── admin.py
│   └── tasks/
│       ├── celery.py
│       └── training.py
├── alembic/
│   ├── env.py (configured for async, imports Base metadata)
│   └── versions/
├── .env
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

# CONFIGURATION (core/config.py)
- Use pydantic-settings BaseSettings
- All values from environment with defaults
- DATABASE_URL: postgresql+asyncpg://user:pass@postgres:5432/recommender
- RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
- RABBITMQ_QUEUE: excursion_events
- REDIS_URL: redis://redis:6379/0
- CELERY_BROKER_URL (same as RABBITMQ_URL)
- CELERY_RESULT_BACKEND: redis://redis:6379/1
- DJANGO_BASE_URL: http://django:8000
- MODEL_PATH: /app/models/
- TOP_K: 20, COLD_START_MIN_INTERACTIONS: 3
- HYBRID_ALPHA: 0.35, POPULARITY_WEIGHT: 0.2
- IALS_FACTORS: 128, IALS_REGULARIZATION: 0.05, IALS_ITERATIONS: 15
- IALS_ALPHA: 2.0, PGVECTOR_INDEX_LISTS: 100

# DATABASE (core/database.py)
- async_engine with asyncpg
- async_sessionmaker with expire_on_commit=False
- async def get_db() -> AsyncGenerator[AsyncSession, None] for FastAPI Depends

# MODELS (SQLAlchemy 2.0 style)
All models use Mapped types and mapped_column. Base = declarative_base()

Excursion:
- id: Mapped[int] = mapped_column(primary_key=True)
- excursion_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
- title: Mapped[str], description: Mapped[str], category: Mapped[str]
- location_type: Mapped[str], price: Mapped[float], duration: Mapped[int]
- average_rating: Mapped[Optional[float]], review_count: Mapped[int]
- popularity: Mapped[int] = mapped_column(default=0)
- text_for_embedding: Mapped[str]
- embedding: Mapped[Optional[list[float]]] via Vector(768)
- ials_factors: Mapped[Optional[list[float]]] via Vector(128)
- has_embedding: Mapped[bool] = mapped_column(default=False)
- last_updated: Mapped[datetime]

UserInteraction:
- id: Mapped[int], user_id: Mapped[Optional[int]], session_id: Mapped[Optional[str]]
- excursion_id: Mapped[int], event_type: Mapped[str]
- weight: Mapped[float], timestamp: Mapped[datetime]

UserProfile:
- user_id: Mapped[int] = mapped_column(primary_key=True)
- content_vector: Mapped[Optional[list[float]]] via Vector(768)
- ials_factors: Mapped[Optional[list[float]]] via Vector(128)
- interaction_count: Mapped[int], last_updated: Mapped[datetime]

RecommendationCache:
- id: Mapped[int], user_id: Mapped[int] = mapped_column(unique=True)
- excursion_ids: Mapped[list[int]] via JSON, scores: Mapped[list[float]] via JSON
- created_at: Mapped[datetime]

SimilarCache:
- id: Mapped[int], excursion_id: Mapped[int] = mapped_column(unique=True)
- similar_ids: Mapped[list[int]] via JSON, scores: Mapped[list[float]] via JSON
- created_at: Mapped[datetime]

TrainingState:
- id: Mapped[int], last_training_time: Mapped[Optional[datetime]]
- total_interactions: Mapped[int], interactions_since_training: Mapped[int]
- retrain_threshold: Mapped[int] = mapped_column(default=100)
- models_ready: Mapped[bool] = mapped_column(default=False)

# ALEMBIC SETUP
- env.py uses run_async with async engine
- target_metadata = Base.metadata
- Migrations run via: docker-compose exec recommender-api alembic upgrade head
- No init_db function — migrations create all tables

# DEPENDENCY INJECTION (core/di.py)
All services are classes. Dependencies are injected via FastAPI Depends.
Example pattern:
- async def get_settings() -> Settings (singleton via lru_cache)
- async def get_db() -> AsyncGenerator[AsyncSession, None]
- async def get_cache_service(db, settings) -> CacheService
- async def get_content_service(db, settings) -> ContentService
- async def get_collaborative_service(db, settings) -> CollaborativeService
- async def get_hybrid_service(db, settings) -> HybridService
- async def get_django_client(settings) -> DjangoClient

# SERVICES
Services accept dependencies in __init__(self, db: AsyncSession, config: Settings).
Do NOT use global singletons for services — use DI.
