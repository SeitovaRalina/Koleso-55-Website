# AI Agent Workflow

## Текущий путь заявки (KOLE-3)

Клиент выбирает экскурсию и слот, указывает ФИО и телефон, затем отправляет заявку. Django создаёт `TourOrder` со статусом `new`; менеджер связывается с клиентом и согласует детали. Отправка заявки не оплачивает заказ и не подтверждает место. Публичные тексты не должны обещать онлайн-оплату или автоматическое подтверждение. Правила YooKassa ниже относятся к будущей интеграции.

Отмена новой заявки не освобождает место в слоте: при создании `new` оно не занималось. Заголовок формы — «Бронь». Строка «Бронх» отсутствует в исходниках; расхождение с production нужно проверить при отдельном релизе.

> Current production and session handover: `docs/AGENT_HANDOVER.md`. It takes
> precedence over stale deployment assumptions in this document, including the
> former “domain not ready” and “deploy later” notes.

Цель: сделать Codex полезным для разработки backend/frontend, проверки интеграции `main_service` и `recommendation_service`, оплаты YooKassa и деплоя.

## Базовые правила

- Корневой источник правил: `AGENTS.md`.
- Ответы короткие: использовать `caveman`.
- Поиск по коду сначала через `ast-index`, затем `rg` только для строк, комментариев, regex или если индекс ничего не нашел.
- Любая задача начинается с чтения локального контекста: README, env example, settings, routes, serializers, models, tests.
- Не менять пользовательские `.env`. Менять только `.env.example` и docs.

## Multica

- Описание проекта хранится в `docs/MULTICA_PROJECT_DESCRIPTION.md`; инструкции агента — в `docs/MULTICA_AGENT_INSTRUCTIONS.md`. Эти файлы служат версионируемым источником настроек Multica Cloud. После изменения файла обновить соответствующее поле в Multica: синхронизация не автоматическая.
- Проект `Koleso 55` использует локальный Git-репозиторий в режиме `worktree`. Агент `Koleso Codex` приватный, максимум один одновременный запуск. Для него задан аргумент Codex `-c windows.sandbox=unelevated`; фактический режим проверять по конфигурации конкретного запуска.
- Одна задача — один проверяемый результат. Назначение агенту вне `backlog` запускает работу. Готовый результат переводить в `in_review`; `done` — после проверки человеком.
- Не помещать секреты и внутренние адреса в описание проекта, инструкции агента или текст задач Multica. Сам Git worktree не является защитой от доступа к остальным файлам пользователя.
- Пул задач группировать по общему пользовательскому сценарию, слоям кода и критериям приёмки. Мелкие взаимосвязанные исправления объединять; независимые или рискованные изменения вести отдельными issue и PR.
- Каждая задача с изменением кода завершается PR по `.github/pull_request_template.md`. Для UI нужны реальные desktop/mobile скриншоты прямо в PR; для backend — тесты, контрактные и интеграционные проверки с фактическими результатами. Отсутствие CI нельзя выдавать за успешный CI.
- Создание PR выполняет `gh` с авторизацией на GitHub; GitHub App Multica только отслеживает PR. Для автоматической связи PR с задачей включить интеграцию GitHub в Multica и добавить ключ issue в заголовок PR. Подключать только нужный репозиторий.
- Вопросы заказчику фиксировать в комментарии issue, ставить `blocked` и продолжать после ответа в том же issue. Ответ в обсуждении агента может запустить следующий run.
- Production-релиз вести отдельной задачей после ревью и объединения проверенного набора PR. Срочный hotfix — отдельное исключение с резервной копией, контролем ресурсов и smoke-проверкой по `docs/AGENT_HANDOVER.md`. Не деплоить автоматически после каждой feature.

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
- Визуальные референсы: current Koleso design system, `manawa.com`, палитра из `frontend/public/hero-bg.jpg`.
- Frontend style: closer to premium editorial current Koleso design system.
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
