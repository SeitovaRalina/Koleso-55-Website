# Recommendation Service Setup Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

## Installation Commands

### 1. Install Poetry (if not already installed)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or via pip
pip install poetry

# Add Poetry to PATH (add to your shell profile)
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Install Dependencies

```bash
# Navigate to recommendation service directory
cd backend/recommendation_service

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Or install without virtual environment (not recommended)
poetry install --no-venv
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```bash
DATABASE_URL=postgresql+asyncpg://recommender_user:recommender_pass@recommender_postgres:5432/recommender
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://recommender_redis:6379/0
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://recommender_redis:6379/1
DJANGO_BASE_URL=http://main_service:8000
```

### 4. Database Setup with Alembic

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Create migration for new changes
alembic revision --autogenerate -m "Add vector indexes"

# Downgrade migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

### 5. Docker Setup

```bash
# Navigate to backend directory
cd backend

# Build and start all services
docker-compose up --build

# Start specific services
docker-compose up recommender_postgres recommender_redis rabbitmq

# Start recommendation service only
docker-compose up recommendation_service recommender_celery_worker

# View logs
docker-compose logs -f recommendation_service
docker-compose logs -f recommender_celery_worker

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Development Commands

### Local Development

```bash
# Start API server locally
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker locally
celery -A app.celery_app worker --loglevel=info

# Start Celery beat for periodic tasks
celery -A app.celery_app beat --loglevel=info

# Start Flower (Celery monitoring)
celery -A app.celery_app flower --port=5555
```

### Code Quality

```bash
# Format code
poetry run black app/
poetry run isort app/

# Lint code
poetry run flake8 app/

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app tests/
```

## API Testing Commands

### Health Check

```bash
# Basic health check
curl http://localhost:8002/api/v1/health/

# Detailed health check
curl http://localhost:8002/health
```

### Recommendations

```bash
# Get user recommendations
curl "http://localhost:8002/api/v1/recommendations/user/42?top_k=20&exclude_interacted=true"

# Get similar items
curl "http://localhost:8002/api/v1/recommendations/similar/15?top_k=10"

# Get popular items
curl "http://localhost:8002/api/v1/recommendations/popular?top_k=20"
```

### Admin Endpoints

```bash
# Trigger model retraining
curl -X POST http://localhost:8002/api/v1/admin/retrain

# Force retraining
curl -X POST "http://localhost:8002/api/v1/admin/retrain?force=true"

# Sync excursions from Django
curl -X POST http://localhost:8002/api/v1/admin/sync-excursions

# Get training status
curl http://localhost:8002/api/v1/admin/training-status
```

## Database Commands

### PostgreSQL

```bash
# Connect to recommendation database
docker exec -it recommender_postgres psql -U recommender_user -d recommender

# Connect via psql locally
psql -h localhost -p 5433 -U recommender_user -d recommender

# Check pgvector extension
\dx

# Check tables
\dt

# Check vector columns
\d excursions
\d user_profiles
```

### Redis

```bash
# Connect to Redis
docker exec -it recommender_redis redis-cli

# Check cache keys
KEYS rec:user:*
KEYS sim:*

# Get cache value
GET rec:user:42

# Clear cache
FLUSHALL
```

## Monitoring Commands

### Service Status

```bash
# Check all services status
docker-compose ps

# Check specific service logs
docker-compose logs recommendation_service
docker-compose logs recommender_celery_worker

# Monitor resource usage
docker stats

# Check RabbitMQ management UI
# Open http://localhost:15672 in browser (guest/guest)
```

### Celery Monitoring

```bash
# Check active tasks
celery -A app.celery_app inspect active

# Check scheduled tasks
celery -A app.celery_app inspect scheduled

# Check stats
celery -A app.celery_app inspect stats

# Purge all tasks
celery -A app.celery_app purge
```

## Troubleshooting Commands

### Common Issues

```bash
# Check if ports are available
netstat -tulpn | grep :8002
netstat -tulpn | grep :5433
netstat -tulpn | grep :6380

# Check Docker containers
docker ps -a

# Restart specific service
docker-compose restart recommendation_service

# Rebuild service
docker-compose up --build recommendation_service

# Check environment variables
docker-compose exec recommendation_service env | grep -E "(DATABASE|RABBITMQ|REDIS)"
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
docker-compose down
docker volume rm backend_recommender_postgres_data
docker-compose up recommender_postgres

# Recreate database
docker exec -it recommender_postgres psql -U recommender_user -d postgres -c "DROP DATABASE IF EXISTS recommender;"
docker exec -it recommender_postgres psql -U recommender_user -d postgres -c "CREATE DATABASE recommender;"
alembic upgrade head
```

### Performance Testing

```bash
# Load test recommendations
ab -n 1000 -c 10 "http://localhost:8002/api/v1/recommendations/user/42/"

# Test health endpoint
ab -n 1000 -c 20 "http://localhost:8002/api/v1/health/"
```

## Production Deployment Commands

### Environment Preparation

```bash
# Set production environment
export ENVIRONMENT=production

# Install production dependencies
poetry install --only=main

# Create production database
alembic upgrade head
```

### Docker Production

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale recommendation_service=2 --scale recommender_celery_worker=3

# Update services
docker-compose pull
docker-compose up -d
```

### Monitoring Production

```bash
# Check service health
curl http://localhost:8002/api/v1/health/

# Monitor logs
docker-compose logs -f --tail=100 recommendation_service

# Check resource usage
docker stats --no-stream
```

## Migration Commands

### Creating New Migrations

```bash
# Generate migration for model changes
alembic revision --autogenerate -m "Add new feature"

# Manually create migration
alembic revision -m "Custom migration"

# Edit migration file
nano alembic/versions/<migration_file>.py
```

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade +1
alembic upgrade 1234abcd

# Downgrade
alembic downgrade -1
alembic downgrade base
```

### Migration Debugging

```bash
# Show SQL for migration
alembic upgrade head --sql

# Dry run migration
alembic upgrade head --dry-run

# Check migration history
alembic history --verbose
```

## Quick Start Summary

```bash
# Complete setup (run in order)
cd backend/recommendation_service
poetry install
cp .env.example .env
# Edit .env with your settings
cd ../..
docker-compose up --build recommender_postgres recommender_redis rabbitmq
# Wait for services to be healthy
docker-compose up recommendation_service recommender_celery_worker
curl http://localhost:8002/api/v1/health/
```
