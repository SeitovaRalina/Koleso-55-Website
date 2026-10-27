# Backend Integration Plan

## Новости (KOLE-7)

Расширение KOLE-7: `/news` показывает только анонсы, обложку и категорию. «Читать далее» ведёт на постоянный `/news/:slug`. Детальная страница показывает упорядоченные блоки `heading`, `paragraph`, `image` и отдельную обложку.

Публичный API: `GET /api/news/?page=N&category=<slug>` возвращает `{count,next,previous,results}`. Элемент списка содержит `title`, `slug`, `excerpt`, `cover`, `published_at`, `category: {name,slug} | null`; полного текста в списке нет. `GET /api/news/categories/` возвращает массив категорий с опубликованными новостями. `GET /api/news/{slug}/` добавляет `blocks: [{kind,position,text,image,alt,caption}]` в порядке `position,pk`. Черновики и будущие записи скрыты во всех публичных ответах.

В Admin редактору нужны `is_staff` и права `view/add/change/delete` только для `news.NewsArticle`, `news.NewsCategory`, `news.NewsBlock`. Категории редактируются отдельно. Блоки редактируются inline в новости, порядок задаётся числом. Поля типа блока проверяются: подзаголовок/абзац требуют текст; изображение требует файл и alt. Миграция `news.0002_categories_and_blocks` переносит прежние строковые категории в отдельную таблицу и старый `body` в первый блок абзаца, не удаляя исходный текст.

## KOLE-5: расписание и отображение цены

`SlotSerializer` в списке и деталях события отдаёт `end_date` и `end_time` (оба `null` для старых слотов). Окончание задаётся парой полей и должно быть позже начала; переход через полночь допустим. Клиент не вычисляет окончание из `Excursion.duration`. Для многодневной программы число календарных дней считается включительно по `Slot.date` и `Slot.end_date`.

Список событий отдаёт `is_multi_day` и `ticket_types` с `is_active`, как и детали. Клиент показывает цену ближайшего доступного слота: `price_override`, если задана, иначе минимальную цену активных тарифов или базовую `Excursion.price` при отсутствии тарифов. При нескольких тарифах выводится «от»; при одном тарифе и выбранном слоте цена точная. Сортировка и фильтр по `price` продолжают использовать базовое поле модели; при изменении тарифов базовую цену нужно поддерживать как индекс каталога.

Цель: стабильно связать Django `main_service`, FastAPI `recommendation_service`, frontend и будущую оплату YooKassa.

Current priority note: frontend production-ready work goes first. Backend pricing, YooKassa, and deploy remain planned later phases.

Current public contract (KOLE-3): `POST /api/bookings/orders/` accepts a guest's name, phone, excursion and slot; it creates `TourOrder` with `status=new`. It does not charge the customer, confirm participation or occupy a seat. The manager contacts the customer to agree on availability and terms. The YooKassa rules below are future integration requirements, not the current public flow.

Update 2026-06-07:

- Local `python manage.py check` in `backend/main_service` currently fails before Django setup because Python cannot import `celery`.
- Cause: backend dependencies are not installed in the active local Python environment, or checks must be run inside the Docker service/venv.
- Demo seed command added for Django:

```powershell
cd backend/main_service
python manage.py migrate
python manage.py seed_demo_data
```

- VK market data was requested as a seed source, but `https://vk.com/market-182407585?screen=group` was not accessible from the current environment. Seed data is synthetic and project-themed.

## Текущее состояние

- Django API: `backend/main_service`.
- Recommender API: `backend/recommendation_service`.
- Общая инфраструктура: PostgreSQL + pgvector, Redis, RabbitMQ.
- Django публикует recommendation events через `analytics.services.publish_recommendation_event`.
- Recommender читает RabbitMQ через `RabbitMQConsumer`.
- Docker compose уже содержит `nginx`, но nginx config нужен в `backend/nginx/nginx.conf`.
- Deployment target: один Timeweb service/VPS для frontend + backend за nginx.
- YooKassa mode: test only.
- Booking is public; auth is optional.
- YooKassa is main payment method after booking.
- Manager contact is fallback.
- Slot is occupied only after payment.
- Prices are backend-owned; `main_service` must support multiple pricing models before payment.

## Найденные риски

- `settings.py` содержит production-risk: `ALLOWED_HOSTS` включает `*`.
- `recommendation_service` CORS разрешает `*` при `allow_credentials=True`.
- Frontend `recommendations.ts` ожидает `Recommendation[]`, но API возвращает response object:
  - `{ recommendations, user_id, session_id, algorithm_used }`
  - `{ similar_excursions, excursion_id, algorithm_used }`
- В booking flow нет payment model и нет статусов платежа.
- `TourOrder.save()` меняет booked participants при смене статуса на `paid`; для платежей это надо защищать от повторного webhook.

## Целевой contract

Public frontend routes:

- Django API через `/api/*`.
- Recommender API через `/api/v1/*`.
- Django admin через `/admin/`.
- Static/media через nginx.

Internal Docker routes:

- `main_service:8000`
- `recommender_api:8000`
- `postgres:5432`
- `redis:6379`
- `rabbitmq:5672`

## Этап 1: стабилизация dev

1. Создать локальный `.env` из `backend/.env.example`.
2. Поднять infra:

```powershell
cd backend
docker compose up -d postgres redis rabbitmq
docker compose up -d main_service recommender_api django_celery_worker recommender_worker
```

3. Проверить health:

```powershell
curl http://localhost:8001/health/
curl http://localhost:8002/health
```

4. Проверить docs:

```powershell
curl http://localhost:8001/api/schema/
curl http://localhost:8001/api/docs/
```

## Этап 2: контрактные проверки recommender

Нужно добавить tests или smoke script:

- Create/view/favorite/booking event publish from Django.
- RabbitMQ consumer receives event.
- Recommender stores interaction.
- `GET /api/v1/recommendations/user/{id}` returns object with `recommendations`.
- `GET /api/v1/similar/{id}` returns object with `similar_excursions`.

Frontend fix:

- unwrap `response.data.recommendations`.
- unwrap `response.data.similar_excursions`.
- align query param: endpoint `/recommendations/` uses `limit`, not `top_k`.

## Этап 3: YooKassa test mode

Добавить Django app `payments` или модуль внутри `bookings`.

Рекомендуется отдельный app:

- `payments/models.py`
- `payments/services/yookassa.py`
- `payments/views.py`
- `payments/urls.py`
- `payments/tests/`

API:

- `POST /api/payments/orders/{order_id}/create/`
- `GET /api/payments/{payment_id}/status/`
- `POST /api/payments/yookassa/webhook/`

Business rules:

- 100% prepayment.
- Do not reserve slot before payment.
- Mark slot participants only after `payment.succeeded`.
- Support guest order payment.
- Compute payment amount on backend.
- Support fixed per-person and adult/child prices.
- Fixed price orders use YooKassa.
- Negotiated/custom price orders use manager fallback until manual payment links are designed.
- Account cancellation allowed only more than 48h before event.
- Late cancellation/refund uses refund request flow.

Подробно: `docs/YOOKASSA_IMPLEMENTATION.md`.

## Этап 4: nginx + Timeweb VPS deploy

1. Использовать `backend/compose.production.yml`; PostgreSQL брать из Timeweb DBaaS.
2. Собирать frontend multi-stage image и раздавать `dist` из nginx.
3. Публиковать только `80/443`; API, Redis и RabbitMQ оставлять во внутренней network.
4. Использовать один HTTPS origin без wildcard hosts/origins.
5. Проверить маршруты `/health/`, `/api/`, `/api/v1/` и `/api/assistant/`.

Подробно: `docs/TIMEWEB_NGINX_DEPLOY.md`.

## Definition of Done

- `docker compose up` поднимает все backend services.
- Health checks green.
- Frontend работает через один public origin.
- Payment create возвращает YooKassa confirmation URL.
- Webhook idempotent.
- Order becomes `paid` only after trusted payment success.
- nginx starts through compose profile `proxy`.

## Homepage Reviews API

- `Review.user` заполнен для отзывов сайта и пуст для ручных отзывов клиента.
  Ручной отзыв хранит `manual_first_name`, `manual_last_name` и
  `is_admin_added=True`. Для отзывов сайта действует уникальность
  `(user, excursion)`; точный дубль ручного отзыва блокируется формой Admin.
- `GET /api/reviews/excursions/{id}/reviews/` возвращает `user_name` из
  имени аккаунта или имени ручного автора. `GET /api/reviews/homepage/`
  возвращает `author_name` по тому же правилу, если не задано
  `homepage_author_name`. Только одобренные отзывы публичны.
- Создание через `POST /api/reviews/` остаётся доступно авторизованному
  пользователю с завершённым заказом; ручное создание доступно только
  сотруднику с правом добавления отзыва в Django Admin.
  Внешний отзыв из Admin сразу получает `approved`; отзыв через API остаётся
  `pending` (либо `rejected` после фильтра). Поля происхождения и статус из
  публичного POST игнорируются. Существующие записи и миграция `0006` не меняются.

- Admin controls homepage inclusion on `Review`:
  - `show_on_homepage`;
  - `homepage_author_name`;
  - `homepage_order`.
- Admin controls review photos in `ReviewImage` inline:
  - `is_homepage_main`;
  - `homepage_order`.
- Main homepage photo priority:
  1. `ReviewImage` with `is_homepage_main=True`, ordered by `homepage_order`;
  2. first review image by `homepage_order`;
  3. legacy `homepage_main_photo`, if present;
  4. main excursion image.
- Public endpoint: `GET /api/reviews/homepage/`.
- Response item:
  - `id`;
  - `author_name`;
  - `rating`;
  - `text`;
  - `main_photo`;
  - `excursion_id`;
  - `excursion_title`;
  - `created_at`.
- Only approved reviews with `show_on_homepage=True` are returned.

## Excursion List API Additions

- `GET /api/excursions/` list items include `nearest_slots`.
- `nearest_slots` contains up to 3 upcoming slots from today, ordered by date/time.
- Homepage event cards use `nearest_slots[0]` for nearest date/time and remaining seats.
- Homepage location search uses `Excursion.LocationType` values and submits `location_type=city|suburban|russia` to catalog.

## Контракт фильтров каталога KOLE-4

`GET /api/excursions/` принимает повторяющиеся `category`, `location_type`, `duration`:

- `category=<slug>`: OR по выбранным категориям; без параметра — все, `category=` — пустой результат.
- `location_type=city|suburban|russia`: OR; неизвестное значение — пустой результат.
- `duration=under_2h|2_to_4h|over_4h`: OR. Диапазоны: `<120`, `120..240`, `>240` минут. Прежние `min_duration`/`max_duration` остаются действительными.
- Разные группы и цена (`min_price`, `max_price`) объединяются через AND.
- `date_from` и `date_to` включительны и должны совпасть с датой одного слота. Можно указать одну границу. Неверный формат даты возвращает 400; обратный диапазон даёт пустой результат.
- Прежние одиночные значения и поиск `search` работают как раньше.
