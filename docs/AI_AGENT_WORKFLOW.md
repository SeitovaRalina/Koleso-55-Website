# AI Agent Workflow

Цель: сделать Codex полезным для разработки backend/frontend, проверки интеграции `main_service` и `recommendation_service`, оплаты YooKassa и деплоя.

## Базовые правила

- Корневой источник правил: `AGENTS.md`.
- Ответы короткие: использовать `caveman`.
- Поиск по коду сначала через `ast-index`, затем `rg` только для строк, комментариев, regex или если индекс ничего не нашел.
- Любая задача начинается с чтения локального контекста: README, env example, settings, routes, serializers, models, tests.
- Не менять пользовательские `.env`. Менять только `.env.example` и docs.

## Как ставить задачу агенту

Хороший prompt:

```text
Используй caveman и ast-index. Реализуй YooKassa create payment для TourOrder.
Не трогай frontend. Обнови .env.example, добавь миграции, тесты webhook idempotency.
Проверка: python manage.py check и pytest/django tests для payments.
```

Плохой prompt:

```text
Сделай оплату.
```

## Рабочий порядок для backend

1. Обновить индекс: `ast-index.cmd update`.
2. Найти затронутые символы: `ast-index.cmd refs "TourOrder"`.
3. Прочитать models/serializers/views/urls/settings.
4. Сформулировать контракт API до правок.
5. Внести минимальный scoped change.
6. Добавить миграции, env vars, docs.
7. Запустить проверки.
8. Сообщить: что изменено, что проверено, какие риски остались.

## Рабочий порядок для интеграции микросервисов

1. Проверить health:
   - Django: `GET /health/`
   - Recommender: `GET /health`
2. Проверить env:
   - `RECOMMENDER_BASE_URL=http://recommender_api:8000` внутри Docker.
   - `VITE_RECOMMENDER_URL` у frontend совпадает с nginx/public route.
3. Проверить очередь:
   - Django публикует event в RabbitMQ.
   - Recommender consumer принимает event.
4. Проверить контракт ответа:
   - frontend не должен ожидать массив, если API возвращает объект.

## Что агент должен уточнять

Уточнять только если без ответа нельзя безопасно продолжить:

- YooKassa shop id и test/live режим.
- Public domain для `return_url` и webhook.
- Нужно ли фискализировать чеки по 54-ФЗ через YooKassa receipts.
- Где должен жить project skill: только в repo `.codex/skills` или глобально.

Текущие решения пользователя:

- Деплой: один сервис/VPS для backend + frontend.
- YooKassa: только test mode.
- Frontend: нужна новая дизайн-система.
- Визуальные референсы: `travelsnob.ru`, `manawa.com`, палитра из `frontend/public/hero-bg.jpg`.
- Frontend style: closer to premium editorial `travelsnob.ru`.
- UI kit: create custom UI kit; do not use shadcn/ui for now.
- Booking: public for guests; auth optional.
- Payment: YooKassa test mode, 100% prepayment, slot occupied only after payment.
- Pricing: backend-owned, multiple models required in `main_service`.
- Negotiated/custom price: offline manager contact.
- Legal DOCX: `frontend/public/documents/`.
- UI kit route: public `/ui-kit`.
- Domain: not ready yet.
- Current implementation order: frontend production-ready first; online payments and deploy later.

Список вопросов для уточнения: `docs/DEVELOPMENT_QUESTIONS.md`.

## Что агент не должен делать

- Не печатать секреты из `.env`.
- Не включать `ALLOWED_HOSTS=*` для production.
- Не выставлять заказ `paid` на frontend callback без webhook/status check.
- Не делать платежи без idempotency.
- Не запускать destructive команды без явного разрешения.
