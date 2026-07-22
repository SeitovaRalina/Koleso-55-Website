# Production Readiness Plan

Цель: подготовить ветку `chore/production-readiness` к безопасному деплою на Timeweb VPS с Timeweb PostgreSQL DBaaS.

Статус этапа: **код и контейнеры готовы; ожидается настройка ресурсов Timeweb**.

## 1. Аудит

- [x] Проверить структуру сервисов, Dockerfiles, Compose, nginx и frontend URL.
- [x] Проверить security settings, SMTP и требования Timeweb DBaaS/pgvector.
- [x] Зафиксировать внешние блокеры.

## 2. Production images

- [x] Запускать Django и assistant через Gunicorn.
- [x] Запускать FastAPI через Uvicorn без reload.
- [x] Собирать frontend multi-stage Dockerfile и копировать `dist` в nginx image.
- [x] Убрать bind mounts исходников.
- [x] Добавить `.dockerignore` во все Docker build contexts.
- [x] Запускать Python-контейнеры от непривилегированного пользователя.

## 3. Production Compose

- [x] Создать `backend/compose.production.yml`.
- [x] Использовать Timeweb DBaaS без PostgreSQL-контейнера.
- [x] Публиковать только порты `80/443`.
- [x] Оставить Redis, RabbitMQ и API во внутренней Docker network.
- [x] Добавить persistent volumes для данных сервисов.
- [x] Использовать общий Chroma volume для vectorizer и assistant.
- [x] Добавить health checks, restart policy и Docker log rotation.
- [x] Ограничить Celery concurrency для экономии RAM.

## 4. Nginx и HTTPS

- [x] Настроить React SPA и маршруты Django, recommender, assistant, static/media.
- [x] Добавить HTTP → HTTPS redirect.
- [x] Подключить host mount для Let's Encrypt.
- [x] Добавить proxy headers, upload limit, rate limit и security headers.
- [ ] Выпустить реальный Let's Encrypt certificate после настройки DNS.

## 5. Application hardening

- [x] Читать hosts, CORS и CSRF origins из environment без production wildcard.
- [x] Отключать debug toolbar при `DEBUG=False`.
- [x] Добавить secure proxy/cookie/HSTS settings.
- [x] Поддержать настраиваемый DB TLS во всех клиентах PostgreSQL; для private-only Timeweb DBaaS использовать `DB_SSLMODE=disable`.
- [x] Настроить SMTP через environment.
- [x] Использовать same-origin frontend URLs.
- [x] Выровнять версии ChromaDB между assistant и vectorizer.
- [x] Загружать тяжёлую profanity model лениво.

## 6. Environment и документация

- [x] Обновить `backend/.env.example`.
- [x] Добавить `backend/.env.production.example`.
- [x] Обновить `docs/TIMEWEB_NGINX_DEPLOY.md`.
- [x] Описать DNS, DBaaS/pgvector, private network, SMTP, backups и rollback.
- [x] Исключить реальные secrets и certificates из Git.

## 7. Verification

- [x] Проверить dev и production Compose через `config --quiet`.
- [x] Выполнить Django и assistant `manage.py check --deploy`.
- [x] Выполнить Django tests.
- [x] Выполнить frontend lint, build и production dependency audit.
- [x] Собрать все production images.
- [x] Проверить nginx syntax.
- [x] Зафиксировать отсутствие recommender pytest suite/dependency.
- [ ] Выполнить полный production smoke с реальными DBaaS и TLS.

## 8. Capacity и внешняя настройка

- [x] Замерить локальный `docker stats --no-stream`.
- [x] Зафиксировать RAM: около 2.5 GiB idle после ограничения workers; 8 GB минимум, 12 GB безопаснее.
- [ ] Проверить доступ VPS к Timeweb DBaaS.
- [ ] Включить `pgvector` в целевой базе и применить migrations.
- [x] Подтвердить с Timeweb: TLS недоступен для private-only DBaaS; CA certificate не требуется.
- [ ] Настроить Timeweb mailbox и проверить SMTP, SPF, DKIM, DMARC.
- [ ] Настроить DNS A/AAAA и выпустить Let's Encrypt certificate.
- [ ] Настроить backup retention для DBaaS, media и Chroma.
- [ ] Выполнить финальный RAM/peak замер на VPS.

## Оставшиеся блокеры

Нужны внешние данные и доступы:

1. Домен и IP VPS.
2. SSH-доступ к VPS.
3. Timeweb DBaaS private host, port, database, application user и password.
4. Включённый `pgvector`.
5. Timeweb mailbox и SMTP password.
6. Yandex API key/folder и production OAuth credentials, если функции включены.
7. Решение по сроку хранения backups.

## Definition of Done этапа

Репозиторная часть выполнена. Полный этап завершится после запуска production Compose на VPS, применения migrations, SMTP-теста, HTTPS smoke-теста и замера peak RAM.
