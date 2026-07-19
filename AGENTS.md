# AGENTS.md

Проект: сайт экскурсий "Колесо путешествий 55".

Эти правила обязательны для AI-агента в этом репозитории.

## Обязательные навыки

- Всегда использовать `caveman` для ответов: кратко, без воды, технически точно.
- Всегда использовать `ast-index` перед поиском по коду, если задача связана со структурой проекта, классами, функциями, роутами, API, зависимостями или рефакторингом.
- После изменений в коде запускать точечную проверку, указанную ниже. Если проверка не запущена, явно написать причину.

## Карта проекта

- `frontend/` - React 19, Vite, TypeScript, TanStack Query, axios.
- `backend/main_service/` - Django 5, DRF, JWT, Celery, PostgreSQL, основной API.
- `backend/recommendation_service/` - FastAPI, SQLAlchemy async, Redis, RabbitMQ, Celery, pgvector.
- `backend/docker-compose.yml` - локальная инфраструктура: Postgres, Redis, RabbitMQ, Django, recommender, nginx.
- `backend/nginx/` - reverse proxy для деплоя.
- `docs/` - рабочие инструкции для AI-агента, интеграции backend, платежей и деплоя.

## Команды

Backend infra:

```powershell
cd backend
docker compose up -d postgres redis rabbitmq
docker compose up -d main_service django_celery_worker django_celery_beat recommender_api recommender_worker
```

Django checks:

```powershell
cd backend/main_service
python manage.py check
python manage.py test
```

Recommendation checks:

```powershell
cd backend/recommendation_service
pytest
alembic upgrade head
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

Search:

```powershell
ast-index.cmd update
ast-index.cmd search "Payment"
ast-index.cmd refs "TourOrder"
```

## Backend правила

- Не читать и не печатать реальные `.env` без явной необходимости. Работать через `.env.example`.
- Секреты не коммитить: `SECRET_KEY`, YooKassa secret key, OAuth secrets, SMTP password.
- Django business state должен меняться транзакционно. Для платежей использовать `transaction.atomic()` и row lock там, где меняется заказ или платеж.
- Внешние платежные запросы должны иметь idempotency key.
- Webhook должен быть идемпотентным: повтор события не должен повторно менять заказ или бронировать места.
- Статус заказа `paid` выставлять только после подтверждения платежа через YooKassa webhook или trusted API status check.
- Бронирование доступно гостям; авторизация опциональна.
- YooKassa test mode - основной путь оплаты после бронирования.
- Предоплата 100%.
- Слот занимать только после успешной оплаты.
- Если цена договорная или экскурсия на заказ, показывать manager fallback.
- Отмена оплаченного заказа из кабинета разрешена только больше чем за 48 часов до события.
- Поздняя отмена идет через заявление на возврат.
- Recommendation event publish не должен ломать основной пользовательский сценарий. Ошибки очереди логировать, но не ронять создание заказа.

## Frontend правила

- Все HTTP-запросы к Django идут через `frontend/src/api/axios.ts`.
- Все HTTP-запросы к recommender должны учитывать реальную форму ответа:
  - `GET /api/v1/recommendations/user/{user_id}` возвращает объект с `recommendations`.
  - `GET /api/v1/recommendations/` возвращает объект с `recommendations`.
  - `GET /api/v1/similar/{excursion_id}` возвращает объект с `similar_excursions`.
- Не добавлять новый UI без проверки mobile и desktop layout.

## Документация

Перед крупной задачей обновить relevant docs:

- `docs/AI_AGENT_WORKFLOW.md`
- `docs/BACKEND_INTEGRATION_PLAN.md`
- `docs/YOOKASSA_IMPLEMENTATION.md`
- `docs/TIMEWEB_NGINX_DEPLOY.md`
- `docs/FRONTEND_DESIGN_SYSTEM.md`
- `docs/DEVELOPMENT_QUESTIONS.md`

## Project Skills

- React/frontend skill: `.codex/skills/koleso-react-frontend/SKILL.md`

## Definition of Done

- Код соответствует текущим паттернам проекта.
- `.env.example` обновлен, если добавлены новые переменные.
- API контракт описан в docs или schema.
- Миграции добавлены для изменений моделей.
- Тесты или checks запущены.
- Для платежей проверены happy path, cancel path, webhook duplicate, webhook unknown payment.
