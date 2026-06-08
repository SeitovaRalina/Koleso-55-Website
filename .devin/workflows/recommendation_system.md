---
description: recommendation
---

Implement a recommendation microservice for a travel excursion booking platform. The main backend is Django REST Framework. The microservice must provide personalized recommendations and similar excursions.

1. TECHNOLOGY STACK
- FastAPI (Python 3.11+)
- PostgreSQL with pgvector extension (store excursion embeddings and latent factors)
- RabbitMQ (as message broker between Django and microservice)
- Redis (as cache only, NOT as message broker)
- Celery (for async tasks: model retraining, profile updates)
- Docker & docker-compose
- Hugging Face Transformers (DeepPavlov/rubert-base-cased) for text embeddings
- implicit library for IALS collaborative filtering
- torch, numpy, scikit-learn, pydantic, aio-pika (for RabbitMQ consumer), httpx (for health checks)

2. DATA MODELS (SQLAlchemy, async)
All tables must be created on startup via metadata.create_all.

Excursion table:
- id: Integer, primary key
- excursion_id: Integer, unique (maps to Django excursion ID)
- title: String
- description: Text
- category: String
- location_type: String
- price: Float
- duration: Integer
- average_rating: Float, nullable
- review_count: Integer, default 0
- popularity: Integer, default 0 (bookings count, updated from Django events)
- text_for_embedding: Text (concatenation: title + " " + description + " " + category)
- embedding: pgvector.VECTOR(768), nullable
- ials_factors: pgvector.VECTOR(128), nullable
- has_embedding: Boolean, default False
- last_updated: DateTime, default now

UserInteraction table:
- id: Integer, primary key
- user_id: Integer, nullable (NULL for guest users)
- session_id: String(100), nullable
- excursion_id: Integer, foreign key to Excursion.excursion_id
- event_type: String, choices: view, long_view, favorite, review, booking
- weight: Float (0.3 for view, 0.7 for long_view, 0.8 for favorite, 0.9 for review, 1.0 for booking)
- timestamp: DateTime

UserProfile table:
- user_id: Integer, primary key
- content_vector: pgvector.VECTOR(768), nullable
- ials_factors: pgvector.VECTOR(128), nullable
- interaction_count: Integer, default 0
- last_updated: DateTime

RecommendationCache table:
- id: Integer, primary key
- user_id: Integer, unique
- excursion_ids: JSON (list of ints)
- scores: JSON (list of floats)
- created_at: DateTime

SimilarCache table:
- id: Integer, primary key
- excursion_id: Integer, unique
- similar_ids: JSON (list of ints)
- scores: JSON (list of floats)
- created_at: DateTime

TrainingState table:
- id: Integer, primary key
- last_training_time: DateTime, nullable
- total_interactions: Integer, default 0
- interactions_since_training: Integer, default 0
- retrain_threshold: Integer, default 100
- models_ready: Boolean, default False

3. CONFIGURATION (via environment variables, with defaults)
- DATABASE_URL: postgresql+asyncpg://user:pass@postgres:5432/recommender
- RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
- RABBITMQ_QUEUE: excursion_events
- REDIS_URL: redis://redis:6379/0
- CELERY_BROKER_URL (same as RABBITMQ_URL)
- CELERY_RESULT_BACKEND: redis://redis:6379/1
- MODEL_PATH: /app/models/
- TOP_K: 20
- HYBRID_ALPHA: 0.35 (weight for content, 1-alpha for collaborative)
- POPULARITY_WEIGHT: 0.2 (weight for popularity in hybrid score)
- COLD_START_MIN_INTERACTIONS: 3
- IALS_FACTORS: 128
- IALS_REGULARIZATION: 0.05
- IALS_ITERATIONS: 15
- IALS_ALPHA: 2.0 (confidence scaling factor)
- PGVECTOR_INDEX_LISTS: 100

4. RABBITMQ INTEGRATION (for receiving events from Django)
DO NOT use HTTP for receiving events. Django publishes events directly to RabbitMQ exchange "excursion_events" with routing key "excursion_events". The microservice consumes these events via a persistent consumer.

On startup, create a RabbitMQ consumer using aio-pika that:
- Connects to RabbitMQ
- Declares exchange "excursion_events" (type: topic, durable=True)
- Declares queue "excursion_events" (durable=True)
- Binds queue to exchange with routing key "excursion_events"
- Starts consuming messages in an asyncio task (background, non-blocking)

Message format from Django:
{
  "event_type": "view" | "long_view" | "favorite" | "review" | "booking" | "content_update" | "popularity_update",
  "user_id": 42 | null,
  "session_id": "uuid-string" | null,
  "item_id": 15,
  "weight": 0.3,
  "timestamp": "2026-05-02T12:00:00Z",
  "duration": 45 | null,
  "source": "search" | null
}

On receiving a message:
1. Validate required fields (event_type, item_id, weight, timestamp)
2. Save to UserInteraction table
3. If user_id is not null:
   - Spawn Celery task: update_user_profile(user_id)
   - Invalidate Redis cache key: "rec:user:{user_id}"
4. Increment TrainingState.interactions_since_training
5. If interactions_since_training >= retrain_threshold:
   - Spawn Celery task: train_ials_model()
6. ACK the message on success, NACK on failure (for retry)

5. DJANGO INTEGRATION (how Django talks to this microservice)
Django sends events via RabbitMQ (NOT HTTP). Django must:
- Use Celery with a task: publish_event(event_data) that sends to RabbitMQ exchange "excursion_events"
- Call this task after: view ends, booking created, favorite toggled, review submitted, excursion content updated

Django receives recommendations via HTTP (synchronous):
- Django views call: GET http://recommender-api:8000/api/v1/recommendations/user/{user_id}/?top_k=20
- Django views call: GET http://recommender-api:8000/api/v1/recommendations/similar/{excursion_id}/?top_k=10
- Use httpx client with timeout=2s and retries=2
- On failure: return empty list (frontend shows nothing instead of error)

Django must provide these data endpoints for the microservice (to be called during /admin/retrain):
- GET http://django:8000/api/internal/excursions/ (returns all excursions with full text descriptions)
- GET http://django:8000/api/internal/excursions/{id}/ (returns single excursion)
- GET http://django:8000/api/internal/popularity/ (returns {excursion_id: bookings_count} dict)

Implement in Django:
- analytics/models.py: ExcursionView model (user FK nullable, excursion FK, session_id, duration_seconds, source, timestamp)
- analytics/views.py: StartViewTrackingView, HeartbeatView, EndViewTrackingView
- analytics/services.py: publish_view_event() which calls Celery task to publish to RabbitMQ
- Frontend: React hook useViewTracking(excursionId, source) that sends POST /api/analytics/view/start/, heartbeats every 15s, and final POST /api/analytics/view/end/

6. API ENDPOINTS (prefix /api/v1)
All endpoints return JSON. Use Pydantic models for request/response schemas.

GET /health
- Returns: {"status": "ok", "models_ready": true/false, "db_connected": true/false, "rabbitmq_connected": true/false}

GET /recommendations/user/{user_id}?top_k=20&exclude_interacted=true
- Logic:
  1. Check Redis cache: "rec:user:{user_id}". If found and fresh (<1h), return immediately.
  2. Get user from UserProfile table. If not found or interaction_count < COLD_START_MIN_INTERACTIONS:
     - Return top-K popular excursions (sorted by popularity desc, limited to top_k).
  3. Get all Excursion records with has_embedding=True and ials_factors IS NOT NULL.
  4. For each excursion, compute:
     content_score = cosine_similarity(user.content_vector, item.embedding)
     collab_score = dot(user.ials_factors, item.ials_factors)
     popularity_score = item.popularity / max_popularity
     final_score = 0.35*content_score + 0.45*collab_score + 0.2*popularity_score
  5. If exclude_interacted=true: filter out excursions with UserInteraction records for this user.
  6. Sort by final_score desc, take top_k.
  7. Cache result in Redis (TTL=3600) and RecommendationCache table.
  8. Return: {"user_id": 42, "recommendations": [{"excursion_id": 15, "score": 0.87, "breakdown": {"content": 0.42, "collab": 0.38, "popularity": 0.07}}]}

GET /recommendations/similar/{excursion_id}?top_k=10
- Logic:
  1. Check Redis cache: "sim:{excursion_id}". If found, return immediately.
  2. Get the excursion's embedding. If not found, return 404.
  3. Find top-K excursions (excluding self) by cosine similarity of embeddings using pgvector:
     "SELECT excursion_id, 1 - (embedding <=> %s::vector) AS similarity FROM excursion WHERE excursion_id != %s AND has_embedding = true ORDER BY embedding <=> %s::vector LIMIT %s"
  4. Cache result in Redis (TTL=86400) and SimilarCache table.
  5. Return: {"excursion_id": 15, "similar": [{"excursion_id": 23, "similarity": 0.94}]}

POST /admin/retrain
- Triggers full pipeline:
  1. Fetch all excursions from Django: GET http://django:8000/api/internal/excursions/
  2. For each excursion missing embedding or with content changed: compute RuBERT embedding
  3. Train IALS model using all UserInteraction records
  4. Save factors to DB
  5. Rebuild all caches (popular, similar for all excursions, recommendations for active users)
  6. Update TrainingState: last_training_time=now, interactions_since_training=0, models_ready=True
- Returns: {"status": "training started", "task_id": "uuid"}

GET /admin/stats
- Returns: TrainingState record (all fields), count of excursions with/without embeddings, total interactions

7. CONTENT COMPONENT (RuBERT)
- Load model once at startup: AutoTokenizer + AutoModel from "DeepPavlov/rubert-base-cased"
- Use mean pooling with attention mask:
  inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
  outputs = model(**inputs)
  attention_mask = inputs['attention_mask']
  token_embeddings = outputs.last_hidden_state
  input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
  embedding = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
  Return embedding[0].detach().numpy() as vector(768)
- Store embedding in pgvector using raw SQL: "UPDATE excursion SET embedding = %s::vector, has_embedding = true WHERE excursion_id = %s"
- On /admin/retrain: check if excursion text changed (compare text_for_embedding stored vs fetched from Django). Only recompute if changed or missing.
- User content profile: select all embeddings for excursions the user interacted with, weighted average by weight:
  "SELECT e.embedding, u.weight FROM user_interaction u JOIN excursion e ON u.excursion_id = e.excursion_id WHERE u.user_id = %s"
  Compute weighted average in Python, store in UserProfile.content_vector via raw SQL.

8. COLLABORATIVE COMPONENT (IALS)
- Build matrices from UserInteraction:
  - Get distinct user_ids and excursion_ids, create mappings: user_index = {user_id: matrix_row_index}, item_index = {excursion_id: matrix_col_index}
  - Initialize sparse matrices: P (preference, shape MxN), C (confidence, shape MxN)
  - For each row in UserInteraction:
    user_idx = user_index[row.user_id]
    item_idx = item_index[row.excursion_id]
    P[user_idx, item_idx] = 1
    C[user_idx, item_idx] = 1 + IALS_ALPHA * row.weight
  - Train: model = AlternatingLeastSquares(factors=IALS_FACTORS, regularization=IALS_REGULARIZATION, iterations=IALS_ITERATIONS, use_gpu=False)
  - model.fit(C, show_progress=False)  # Note: implicit expects confidence-weighted matrix
  - Save model to disk: joblib.dump(model, MODEL_PATH + "ials_model.pkl")
  - Extract factors: user_factors = model.user_factors, item_factors = model.item_factors
  - Save item_factors to Excursion table: "UPDATE excursion SET ials_factors = %s::vector WHERE excursion_id = %s"
  - Save user_factors to UserProfile table: "INSERT INTO user_profile (user_id, ials_factors) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET ials_factors = %s"
  - Map matrix indices back to real IDs using the mapping dicts.

9. CACHING STRATEGY (Redis only)
- "rec:user:{user_id}" → JSON of recommendation list, TTL=3600
- "sim:{excursion_id}" → JSON of similar list, TTL=86400
- "pop:popular" → JSON of top-100 popular excursion IDs, TTL=3600 (rebuilt after retrain)
- "meta:max_popularity" → integer or float, TTL=3600
- Invalidate user cache on new event: delete "rec:user:{user_id}" in the RabbitMQ consumer
- Invalidate all user caches after retrain: scan and delete "rec:user:*" keys

10. ASYNC TASKS (Celery, defined in tasks/train_tasks.py and tasks/maintenance.py)
- update_user_profile(user_id): recompute content_vector, update UserProfile, return nothing
- train_ials_model(): full training pipeline, update DB and cache, set TrainingState.models_ready=True
- rebuild_all_caches(): recompute popular, all similar, and active user recommendations
- check_data_integrity(): verify all excursions have embeddings, all active users have profiles

11. INFRASTRUCTURE (docker-compose.yml)
Services:
- postgres: pgvector/pgvector:pg16 image, volume for data, port 5432
- redis: redis:7-alpine image, volume for data, port 6379
- rabbitmq: rabbitmq:3-management-alpine image, ports 5672 (AMQP) and 15672 (management UI)
- recommender-api: FastAPI on uvicorn, port 8000, depends_on=[postgres, redis, rabbitmq]
- recommender-worker: Celery worker, depends_on=[postgres, redis, rabbitmq]

12. PROJECT STRUCTURE
/recommendation_service
  main.py (FastAPI app creation, startup/shutdown events for RabbitMQ consumer)
  config.py (settings from environment)
  database.py (async SQLAlchemy engine and session)
  models.py (SQLAlchemy ORM models)
  schemas.py (Pydantic request/response models)
  routers/
    recommendations.py
    similar.py
    admin.py
  services/
    content_service.py (RuBERT model loading, embedding computation, user profile)
    collaborative_service.py (IALS training and inference)
    hybrid_service.py (scoring with formula from section 7)
    event_consumer.py (RabbitMQ consumer using aio-pika, message processing)
    django_client.py (httpx client to fetch data from Django)
    cache_service.py (Redis get/set/delete helpers)
  tasks/
    celery_app.py (Celery instance)
    train_tasks.py (update_user_profile, train_ials_model, rebuild_all_caches)
  utils/
    pgvector_utils.py (helpers for vector operations with pgvector)
  poetry.lock
  pyproject.toml
  Dockerfile

13. IMPORTANT NOTES
- ALL database operations must use async (asyncpg driver, SQLAlchemy async session).
- On FastAPI startup: create tables (metadata.create_all), load RuBERT model, start RabbitMQ consumer as background task.
- On FastAPI shutdown: close RabbitMQ connection, close DB connection.
- pgvector index: CREATE INDEX IF NOT EXISTS excursion_embedding_idx ON excursion USING ivfflat (embedding vector_cosine_ops) WITH (lists = {PGVECTOR_INDEX_LISTS});
- pgvector index: CREATE INDEX IF NOT EXISTS excursion_ials_idx ON excursion USING ivfflat (ials_factors vector_cosine_ops) WITH (lists = {PGVECTOR_INDEX_LISTS});
- The microservice must be self-contained: `docker-compose up` starts everything and it works.
- Log all errors with full traceback to stderr (JSON structured format).
