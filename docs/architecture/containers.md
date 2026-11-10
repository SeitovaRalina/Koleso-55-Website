# Architecture: containers

- Last verified: 2026-11-08
- Evidence: `AGENTS.md`
- Owner: agent, after direct code/configuration evidence

| Container | Responsibility | Location |
| --- | --- | --- |
| Frontend | React public UI, routing, API clients | `frontend/` |
| Main service | Django domain, Admin, DRF API, auth, bookings, reviews, wishlist, analytics | `backend/main_service/` |
| Django workers | Main-service Celery worker and scheduler | `backend/docker-compose.yml` |
| Recommender API/worker | Personalized/similar results, model training and caches | `backend/recommendation_service/` |
| Assistant | RAG/chat HTTP API with Chroma persistence | `backend/assistant_service/` |
| Vectorizer | Queue consumer that vectorises assistant material | `backend/vectorizer/` |
| Infrastructure | PostgreSQL, Redis, RabbitMQ and nginx | `backend/*compose*.yml`, `backend/nginx/`, `frontend/nginx/` |

Detailed APIs belong in their schema or `docs/api/`; do not duplicate models or
route lists here.
