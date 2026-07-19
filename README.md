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

## Agent Docs

- `AGENTS.md` - обязательные правила для Codex/AI-агента в репозитории.
- `docs/AI_AGENT_WORKFLOW.md` - рабочий процесс для задач агенту.
- `docs/BACKEND_INTEGRATION_PLAN.md` - план интеграции `main_service`, `recommendation_service`, frontend.
- `docs/YOOKASSA_IMPLEMENTATION.md` - план реализации YooKassa.
- `docs/TIMEWEB_NGINX_DEPLOY.md` - nginx и деплой на Timeweb.
- `docs/FRONTEND_DESIGN_SYSTEM.md` - дизайн-система frontend.
- `docs/DEVELOPMENT_QUESTIONS.md` - вопросы по продукту, оплате, frontend, backend, деплою.
- `docs/PRODUCT_DECISIONS.md` - принятые продуктовые и бизнес-решения.
- `docs/NEXT_STEPS.md` - рекомендуемый порядок реализации.
- `.codex/skills/koleso-react-frontend/SKILL.md` - project skill для React/frontend задач.
