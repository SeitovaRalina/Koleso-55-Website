# Project overview

- Last verified: 2026-11-08
- Evidence: `AGENTS.md`, `docs/product/business-rules.md`
- Owner: project owner

`Колесо путешествий 55` — website for excursion discovery, booking, custom
tour requests, gift certificates and customer account workflows.

Core application areas:

- React/Vite frontend in `frontend/`;
- Django/DRF primary API in `backend/main_service/`;
- FastAPI recommendation service in `backend/recommendation_service/`;
- Django RAG/chat assistant in `backend/assistant_service/`;
- Celery vectorisation worker in `backend/vectorizer/`;
- PostgreSQL, Redis, RabbitMQ and nginx through Docker Compose.

Durable product decisions are canonical in `docs/product/`. Deployment facts
and procedures are canonical in `docs/operations/`.
