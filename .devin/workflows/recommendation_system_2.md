Implement a recommendation microservice for a travel excursion booking platform. The main backend is Django REST Framework with RabbitMQ as message broker. Develop in sequential stages, each producing a working result.

TECHNOLOGY STACK
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

PROJECT STRUCTURE
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

CONFIGURATION (core/config.py)
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

DATABASE (core/database.py)
- async_engine with asyncpg
- async_sessionmaker with expire_on_commit=False
- async def get_db() -> AsyncGenerator[AsyncSession, None] for FastAPI Depends

MODELS (SQLAlchemy 2.0 style)
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

ALEMBIC SETUP
- env.py uses run_async with async engine
- target_metadata = Base.metadata
- Migrations run via: docker-compose exec recommender-api alembic upgrade head
- No init_db function — migrations create all tables

DEPENDENCY INJECTION (core/di.py)
All services are classes. Dependencies are injected via FastAPI Depends.
Example pattern:
- async def get_settings() -> Settings (singleton via lru_cache)
- async def get_db() -> AsyncGenerator[AsyncSession, None]
- async def get_cache_service(db, settings) -> CacheService
- async def get_content_service(db, settings) -> ContentService
- async def get_collaborative_service(db, settings) -> CollaborativeService
- async def get_hybrid_service(db, settings) -> HybridService
- async def get_django_client(settings) -> DjangoClient

Services accept dependencies in __init__(self, db: AsyncSession, config: Settings).
Do NOT use global singletons for services — use DI.

STAGE 1: DJANGO PREPARATION (implement in Django project)
Must be done before microservice development.

ExcursionView model:
- user (FK to CustomUser, nullable), excursion (FK to Excursion)
- session_id (CharField, db_index=True), duration_seconds (PositiveIntegerField)
- source (CharField, choices: search/catalog/recommendation/similar/direct)
- started_at (DateTimeField), processed_for_recommendations (BooleanField)

API endpoints in Django:
- POST /api/analytics/view/start/ — creates record, returns {view_id}
- POST /api/analytics/view/heartbeat/ — updates duration_seconds += elapsed
- POST /api/analytics/view/end/ — sets final duration, publishes to RabbitMQ if >5s

Celery task for event publishing:
- publish_event(event_data) sends JSON to RabbitMQ exchange 'excursion_events' with routing_key 'excursion_events'
- Queue is durable, exchange is topic type

Internal API for microservice:
- GET /api/internal/excursions/ — all excursions with full descriptions
- GET /api/internal/popularity/ — {excursion_id: bookings_count}

STAGE 2: MICROSERVICE SKELETON
Implement project structure, config, database, models, DI, migrations.

main.py:
- Create FastAPI app with lifespan
- On startup: create async engine, create async sessionmaker, run alembic migrations programmatically, start RabbitMQ consumer as asyncio background task
- On shutdown: close RabbitMQ, close DB engine
- Include routers with prefix /api/v1

RabbitMQ consumer (services/consumer.py):
- RabbitMQConsumer class with async consume() method
- On message: parse JSON, validate schema, save to UserInteraction, spawn Celery task update_user_profile, invalidate Redis cache, ack/nack
- Background task started in lifespan

Django client (services/django_client.py):
- DjangoClient class with httpx.AsyncClient
- async fetch_excursions() -> list[dict]
- async fetch_popularity() -> dict[int, int]
- Retry logic: 2 retries with exponential backoff

Admin router endpoints:
- POST /admin/retrain — triggers Celery task (placeholder in Stage 2)
- GET /admin/stats — returns TrainingState

Health endpoint:
- GET /health — returns {status, db_connected, rabbitmq_connected, models_ready}

STAGE 3: CONTENT COMPONENT + SIMILAR ENDPOINT
ContentService:
- Load RuBERT model once in __init__ (use asyncio.Lock for thread safety)
- async compute_embedding(text: str) -> list[float]
- Mean pooling with attention mask
- async update_excursion_embedding(excursion_id: int)
- async compute_user_profile(user_id: int) -> list[float] — weighted average of interacted excursions' embeddings

Similar endpoint:
- GET /recommendations/similar/{excursion_id}?top_k=10
- Check Redis cache first (key: sim:{excursion_id})
- If not cached: query pgvector with cosine distance, cache result (TTL=86400), return

Celery tasks for Stage 3:
- update_user_profile(user_id): recompute content_vector, save to UserProfile

STAGE 4: COLLABORATIVE + HYBRID ENDPOINT
CollaborativeService:
- async train()
  1. Get all UserInteraction records
  2. Build user_index and item_index mappings
  3. Build sparse confidence matrix C
  4. Train AlternatingLeastSquares(factors=128, reg=0.05, iterations=15)
  5. model.fit(C)
  6. Save item_factors to Excursion, user_factors to UserProfile
  7. Update TrainingState
- async predict(user_id: int, item_id: int) -> float

HybridService:
- async score(user_id: int, item_id: int) -> dict with content_score, collab_score, popularity_score, final_score
- Formula: final = 0.35*content + 0.45*collab + 0.2*popularity
- Cosine similarity for content, dot product for collab, normalized popularity

Recommendations endpoint:
- GET /recommendations/user/{user_id}?top_k=20&exclude_interacted=true
- Check Redis cache first (key: rec:user:{user_id})
- If user has < COLD_START_MIN_INTERACTIONS: return top popular
- Otherwise: compute hybrid score for all excursions with embeddings, filter out interacted, sort, take top_k, cache (TTL=3600), return

Celery tasks for Stage 4:
- train_ials_model(): full training pipeline
- rebuild_all_caches(): recompute popular, all similar, top active user recommendations

STAGE 5: PRODUCTION READY
Admin endpoint:
- POST /admin/retrain — triggers train_ials_model() Celery task, returns task_id
- GET /admin/stats — returns TrainingState + excursion counts + active user count

Docker Compose:
Services: postgres (pgvector/pgvector:pg16), redis (redis:7-alpine), rabbitmq (rabbitmq:3-management-alpine), recommender-api (uvicorn), recommender-worker (celery)
Networks, volumes for persisted data, healthchecks with interval

pgvector indexes (created in alembic migration):
- IVFFlat index on embedding with vector_cosine_ops
- IVFFlat index on ials_factors with vector_cosine_ops

Logging:
- Structlog or python-json-logger
- Log every API request with duration, errors with traceback
- Log training start/end with metrics

ONE .ENV FILE for all services in backend/ root directory.
DJANGO_ADMIN INTEGRATION FOR MICROSERVICE:
Add Django admin actions that call microservice admin endpoints via HTTP:
- "Retrain model" button -> POST http://recommender-api:8000/api/v1/admin/retrain
- Show stats widget -> GET http://recommender-api:8000/api/v1/admin/stats
No separate admin panel UI — Swagger UI at /docs is sufficient.
