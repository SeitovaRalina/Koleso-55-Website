# Колесо путешествий 55

Монорепозиторий для сайта экскурсий и туризма в Омске и Омской области.

Frontend: React + Vite + Tailwind
Backend: Django 5 + Django REST Framework + PostgreSQL
AI-помощник: LangChain + ChromaDB + LLM

## Repository Structure

- `frontend/` — React/Vite client.
- `backend/main_service/` — main Django API.
- `backend/recommendation_service/` — FastAPI recommendation service.
- `backend/assistant_service/` — Django AI assistant service.
- `backend/vectorizer/` — Celery vectorization worker.
- `backend/docker-compose.yml` — local backend orchestration.
- `docs/` — architecture, integration, and deployment notes.

Assistant ChromaDB files are runtime data. Docker stores them in the
`assistant_chroma_data` named volume; they are not kept in repository root.

## Documentation

Start with `docs/INDEX.md`. It routes product, architecture, API, operations
and development questions without loading obsolete plans. Agent rules are in
`AGENTS.md`; active task context is in `harness/`; delivery evidence is in
`reports/`.
