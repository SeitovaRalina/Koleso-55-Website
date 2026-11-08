# AGENTS.md

Проект: сайт экскурсий "Колесо путешествий 55".

Эти правила обязательны для AI-агента в этом репозитории.

## Обязательные навыки

- Всегда использовать `caveman` для ответов: кратко, без воды, технически точно.
- Всегда использовать `ast-index` перед поиском по коду, если задача связана со структурой проекта, классами, функциями, роутами, API, зависимостями или рефакторингом.
- После изменений в коде запускать точечную проверку, указанную ниже. Если проверка не запущена, явно написать причину.

## Планирование продуктовых изменений

- Не начинать реализацию новой продуктовой функциональности или менять согласованный UX по собственной инициативе.
- Сначала подготовить подробный план: пользовательский сценарий, данные и API, статусы, Admin, UX, миграции, тесты и критерии приёмки.
- После планирования обязательно создать `reports/plan-<slug>.md` по шаблону в `reports/README.md`. Его статус — `draft` до утверждения.
- Реализацию начинать только после явного подтверждения пользователем именно этого плана и фиксации статуса `approved` в plan-report.
- После реализации создать `reports/implementation-<slug>.md`: фактический scope, миграции/API, deliberate deviations и ограничения.
- `reports/testing-<slug>.md` и `reports/review-<slug>.md` обязательны для product/code/API/миграций, Admin, runtime-конфигурации, UI, merge или deploy. Для documentation-only/low-risk задач — только если проверка выявила риск, пользователь запросил их или задача идёт в merge/deploy.
- После product/code изменений обязательны проверка, E2E там, где применимо, и review результата с пользователем до merge/deploy. Без implementation-, testing- и review-report merge/deploy запрещены.

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

### Карта контекста

Перед нетривиальной задачей читать контекст постепенно:

1. `AGENTS.md` — обязательные правила.
2. `harness/README.md`, `docs/project/current-state.md` и карточку активной
   задачи, если она есть.
3. Только связанные с задачей документы из `docs/`, ADR и код, найденный через
   `ast-index`.

`docs/` — долговременный источник истины; `harness/` — краткий активный
контекст; `reports/` — доказательства планирования, реализации, тестов и
review. Не читать целые архивы задач и отчётов без ссылки из активной задачи.
Статусы задач ведутся в Multica; локальные task-файлы содержат только scope,
решения и ссылки.

### Production access

Для deploy/production-задачи прочитать `docs/operations/production.md` и,
если файл существует, локальный gitignored
`docs/operations/production-local.md`. Последний хранит private infrastructure
coordinates only; never commit, copy into reports/Multica or print credentials.
Если local handover отсутствует, не угадывать production access и запросить
у владельца актуальный путь/доступ.

Перед крупной задачей обновить relevant docs:

- `docs/development/workflow.md`
- `docs/architecture/components.md` and `docs/api/contracts.md`
- `docs/product/business-rules.md`, `docs/product/payments.md`, `docs/product/design-system.md`
- `docs/operations/production.md`
- `docs/product/open-questions.md`

## Project Skills

- React/frontend skill: `.codex/skills/koleso-react-frontend/SKILL.md`

## Definition of Done

- Код соответствует текущим паттернам проекта.
- `.env.example` обновлен, если добавлены новые переменные.
- API контракт описан в docs или schema.
- Миграции добавлены для изменений моделей.
- Тесты или checks запущены.
- Для платежей проверены happy path, cancel path, webhook duplicate, webhook unknown payment.
