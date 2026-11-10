# Local development

- Last verified: 2026-11-08
- Evidence: root `AGENTS.md`, `backend/docker-compose.yml`, package manifests
- Owner: agent

## Prerequisites

- Docker Desktop/Engine for infrastructure and services;
- Python environment matching each service manifest;
- Node/npm for `frontend/`;
- local configuration created from approved examples only. Do not publish
  actual environment values.

## Normal start

```powershell
cd backend
docker compose up -d postgres redis rabbitmq
docker compose up -d main_service django_celery_worker django_celery_beat recommender_api recommender_worker
```

Assistant and vectorizer are separate services in the same compose file. Start
them only when task requires chat/RAG/vectorisation:

```powershell
cd backend
docker compose up -d assistant_service vectorizer_worker
```

Frontend development:

```powershell
cd frontend
npm run dev
```

## Basic checks

```powershell
cd backend/main_service
python manage.py check
python manage.py test

cd ../../frontend
npm run lint
npm run build
```

Recommender checks and migrations are task-specific:

```powershell
cd backend/recommendation_service
pytest
alembic upgrade head
```

Check actual container health before assuming services run. Do not run schema
migrations against production from this guide.
