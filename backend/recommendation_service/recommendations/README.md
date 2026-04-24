# Excursion Recommendation Microservice

A Django-based microservice system for recommending excursions based on user preferences and collaborative filtering.

## Architecture

The system consists of the following services:

1. **Main Service** (Port 8001) - Django API for managing users and excursions
2. **Worker Service** - Processes excursion descriptions and creates vector embeddings using RuBERT
3. **Recommendation Service** (Port 8002) - Provides personalized recommendations
4. **PostgreSQL** - Stores user data, excursions, and visit history
5. **ChromaDB** - Vector database for similarity search
6. **RabbitMQ** - Message queue for asynchronous processing

## Services

### Main Service API Endpoints

- `POST /api/users/` - Create a new user
- `GET /api/users/list/` - Get all users
- `POST /api/excursions/` - Add a new excursion (triggers vectorization)
- `GET /api/excursions/list/` - Get all active excursions
- `POST /api/excursions/visited/` - Mark an excursion as visited by a user
- `GET /api/users/{user_id}/excursions/` - Get user's visited excursions

### Recommendation Service API Endpoints

- `GET /api/recommendations/{user_id}/` - Get personalized recommendations for a user
- `GET /api/health/` - Health check endpoint

## Recommendation Algorithm

The recommendation system uses a weighted combination of:

1. **Cosine Similarity (35%)** - Content-based similarity using RuBERT embeddings
2. **Matrix Similarity (65%)** - Collaborative filtering based on user behavior patterns

The formula: `final_score = 0.35 * cosine_similarity + 0.65 * matrix_similarity`

## Setup and Running

### Prerequisites

- Docker and Docker Compose
- Git

### Quick Start

1. Clone the repository and navigate to the project directory
2. Run the services:
   ```bash
   docker-compose up --build
   ```

3. The services will be available at:
   - Main Service: http://localhost:8001
   - Recommendation Service: http://localhost:8002
   - RabbitMQ Management: http://localhost:15672 (guest/guest)
   - ChromaDB: http://localhost:8000

### Database Setup

The PostgreSQL database will be automatically created and migrated when you run `docker-compose up`.

## Usage Example

1. Create a user:
   ```bash
   curl -X POST http://localhost:8001/api/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "john", "email": "john@example.com"}'
   ```

2. Add an excursion:
   ```bash
   curl -X POST http://localhost:8001/api/excursions/ \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Historical City Tour",
       "description": "A comprehensive tour of the city's historical landmarks",
       "short_description": "Explore the rich history of our city",
       "location": "City Center",
       "duration": 120,
       "price": "50.00"
     }'
   ```

3. Mark as visited:
   ```bash
   curl -X POST http://localhost:8001/api/excursions/visited/ \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "excursion_id": 1,
       "rating": 5
     }'
   ```

4. Get recommendations:
   ```bash
   curl http://localhost:8002/api/recommendations/1/
   ```

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **Database**: PostgreSQL 15
- **Vector Database**: ChromaDB
- **Message Queue**: RabbitMQ
- **ML Model**: RuBERT-tiny2 (cointegrated/rubert-tiny2)
- **Containerization**: Docker & Docker Compose
- **ML Libraries**: Transformers, PyTorch, scikit-learn

## Development

### Running Individual Services

To run individual services for development:

```bash
# Main Service
cd main_service
python manage.py runserver

# Recommendation Service
cd recommendation_service
python manage.py runserver

# Worker
cd worker
python worker.py
```

### Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `RABBITMQ_URL` - RabbitMQ connection string
- `CHROMADB_URL` - ChromaDB connection string

## Monitoring

- RabbitMQ Management UI: http://localhost:15672
- ChromaDB UI: http://localhost:8000

## License

This project is licensed under the MIT License.
