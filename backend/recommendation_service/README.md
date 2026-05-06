# Recommendation Service

A FastAPI microservice providing personalized recommendations for travel excursions using hybrid collaborative filtering and content-based methods.

## Architecture

- **FastAPI** - REST API framework
- **PostgreSQL** with **pgvector** - Vector database for embeddings and latent factors
- **Redis** - Caching layer
- **RabbitMQ** - Message broker for receiving events from Django
- **Celery** - Async task processing for model training and profile updates

## Features

- Personalized excursion recommendations
- Similar item recommendations
- Content-based filtering using BERT embeddings
- Collaborative filtering using IALS algorithm
- Real-time event processing from Django
- Automated model retraining
- Caching for performance

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Environment Setup

1. Copy environment configuration:
```bash
cp .env.example .env
```

2. Review and update `.env` with your specific configuration.

### Running with Docker

1. Build and start all services:
```bash
docker-compose up --build
```

2. Wait for all services to be healthy (check logs):
```bash
docker-compose logs -f
```

3. The API will be available at `http://localhost:8001`
4. RabbitMQ Management UI: `http://localhost:15673` (guest/guest)
5. PostgreSQL: `localhost:5433`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start dependencies with Docker:
```bash
docker-compose up postgres redis rabbitmq -d
```

3. Run the API:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Run Celery worker (in separate terminal):
```bash
celery -A app.celery_app worker --loglevel=info
```

## API Endpoints

### Health Check
```
GET /api/v1/health/
```

### Recommendations
```
GET /api/v1/recommendations/user/{user_id}?top_k=20&exclude_interacted=true
GET /api/v1/recommendations/similar/{excursion_id}?top_k=10
GET /api/v1/recommendations/popular?top_k=20&category=adventure
```

### Admin
```
POST /api/v1/admin/retrain?force=false
POST /api/v1/admin/sync-excursions
GET /api/v1/admin/training-status
```

## Database Schema

### Core Tables

- **excursions** - Excursion data with embeddings and IALS factors
- **user_interactions** - User interaction events (views, bookings, etc.)
- **user_profiles** - User preference vectors and interaction counts
- **recommendation_cache** - Cached user recommendations
- **similar_cache** - Cached similar item recommendations
- **training_state** - Model training status and metrics

## Integration with Django

### Event Flow (Django → Recommendation Service)

1. Django publishes events to RabbitMQ exchange `excursion_events`
2. Recommendation service consumes events and updates user interactions
3. Celery tasks update user profiles and trigger model training
4. Django requests recommendations via HTTP API

### Event Format
```json
{
  "event_type": "view|long_view|favorite|review|booking",
  "user_id": 42,
  "session_id": "uuid-string",
  "item_id": 15,
  "weight": 0.3,
  "timestamp": "2026-05-02T12:00:00Z"
}
```

### Django Integration Required

Add to Django:

1. **Analytics Model** (`analytics/models.py`):
```python
class ExcursionView(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100)
    duration_seconds = models.IntegerField()
    source = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
```

2. **Celery Task** to publish events to RabbitMQ
3. **API Endpoints** for excursion data sync
4. **Frontend Hook** for view tracking

## Model Training

### Automatic Training

- Triggers when `interactions_since_training >= retrain_threshold`
- Default threshold: 100 interactions
- Runs in background via Celery

### Manual Training

```bash
curl -X POST http://localhost:8001/api/v1/admin/retrain?force=true
```

### Training Process

1. Sync excursion data from Django
2. Generate BERT embeddings for excursion text
3. Train IALS collaborative filtering model
4. Update user profiles with new factors
5. Clear relevant caches

## Configuration

### Key Settings

- `TOP_K`: Number of recommendations (default: 20)
- `HYBRID_ALPHA`: Weight for content-based filtering (default: 0.35)
- `IALS_FACTORS`: Number of latent factors (default: 128)
- `RETRAIN_THRESHOLD`: Interactions before retraining (default: 100)

### Performance Tuning

- Adjust `PGVECTOR_INDEX_LISTS` for vector search performance
- Tune Redis TTL values based on traffic patterns
- Scale Celery workers based on training load

## Monitoring

### Health Checks

The `/api/v1/health/` endpoint returns:
- Database connection status
- RabbitMQ connection status  
- Redis connection status
- Model readiness status

### Logs

- Application logs: `docker-compose logs recommendation-api`
- Celery logs: `docker-compose logs celery-worker`
- Database logs: `docker-compose logs postgres`

## Development Tips

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/
```

### Database Migrations

The service uses SQLAlchemy auto-creation, but for production consider Alembic migrations.

## Troubleshooting

### Common Issues

1. **Models not ready**: Check training status and trigger manual retraining
2. **No recommendations**: Verify excursions have embeddings and user has interactions
3. **Slow responses**: Check Redis cache and vector index performance
4. **RabbitMQ errors**: Verify exchange and queue configuration

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## Production Deployment

### Scaling

- API: Horizontal scaling behind load balancer
- PostgreSQL: Read replicas for recommendation queries
- Redis: Cluster for high availability
- Celery: Multiple workers for training tasks

### Security

- Use environment variables for secrets
- Enable authentication between services
- Configure firewall rules
- Monitor resource usage

### Backup

- Regular PostgreSQL backups
- Redis persistence configuration
- Model file backups to S3/external storage
