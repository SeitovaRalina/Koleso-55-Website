# Timeweb VPS Production Deploy

Цель: frontend, Django, recommender и assistant на одном Timeweb VPS через Docker Compose и nginx. PostgreSQL работает в Timeweb DBaaS.

Production manifest: `backend/compose.production.yml`.

## Architecture

Public:

- `80/tcp` — redirect на HTTPS;
- `443/tcp` — nginx + React frontend;
- `22/tcp` — SSH, желательно только с доверенных IP.

Internal Docker network:

- `main_service:8000` — Django;
- `recommender_api:8000` — FastAPI;
- `assistant_service:8000` — assistant;
- `redis:6379`;
- `rabbitmq:5672`;
- Celery workers.

External managed service:

- Timeweb PostgreSQL DBaaS в одной private network с VPS и extension `pgvector`.

Public routes:

- `/` → React SPA;
- `/api/*` → Django;
- `/admin/*` → Django admin;
- `/health/` → Django health;
- `/api/v1/*` → recommender;
- `/api/assistant/*` → assistant `/v1/*`;
- `/static/*` → Django collected static;
- `/media/*` → Django uploaded media.

## 1. VPS sizing

Локальный idle-замер показал около **6.1 GiB** с автоматическим Celery concurrency и около **2.5 GiB** после ограничения workers до concurrency 1. ML-модели загружаются позже, поэтому peak будет выше idle. Итог: **8 GB RAM — допустимый минимум**, безопасная стартовая рекомендация — **12 GB RAM**, 4 vCPU и 40–60 GB SSD. 4 GB VPS недостаточен.

После первого запуска проверить:

```bash
docker stats --no-stream
free -h
df -h
```

Если peak usage близок к RAM, увеличить VPS. Swap может смягчить краткий peak, но не заменяет RAM для ML workloads.

## 2. DNS

В Timeweb:

1. Добавить `A` record корневого домена на IPv4 VPS.
2. Добавить `A` record `www` на тот же IPv4 либо `CNAME www` на корневой домен.
3. Добавлять `AAAA` только если VPS действительно настроен для IPv6.
4. Дождаться обновления DNS.

Проверка:

```bash
dig +short example.com A
dig +short www.example.com A
```

## 3. Timeweb PostgreSQL DBaaS

1. Создать PostgreSQL 16+ cluster и базу.
2. Создать отдельного application user, не использовать административного пользователя постоянно.
3. Включить `pgvector` для нужной базы: база → Configuration → Extensions.
4. Подключить DBaaS и VPS к private network `192.168.0.0/24`.
5. Для текущего private-only кластера использовать приватный IP `192.168.0.5`.
6. Timeweb подтвердил: защищённое подключение по домену доступно только для кластера с public IP. Поэтому private-only подключение работает без PostgreSQL TLS внутри изолированной сети:

```env
DB_HOST=192.168.0.5
DB_SSLMODE=disable
```

Это не влияет на HTTPS сайта: browser → nginx защищается отдельным Let's Encrypt certificate. Не включать public DB IP только ради TLS; публичный PostgreSQL увеличивает поверхность атаки.

`DATABASE_URL` нужен recommender. Если DB password содержит специальные URL-символы, percent-encode password внутри URL. `DB_PASSWORD` для Django остаётся обычным значением.

Timeweb DBaaS поддерживает `pgvector`; Alembic migration также выполняет `CREATE EXTENSION IF NOT EXISTS vector`.

## 4. Timeweb mail

1. Добавить домен в разделе «Домены и SSL».
2. Подключить «Корпоративную почту».
3. Создать ящик, например `noreply@example.com`.
4. Проверить MX, SPF и DKIM. При сторонних NS добавить records вручную.
5. Использовать SMTP:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.timeweb.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=change-me
DEFAULT_FROM_EMAIL=noreply@example.com
SERVER_EMAIL=noreply@example.com
```

Timeweb требует SMTP authorization; sender должен совпадать с authenticated mailbox.

## 5. VPS base setup

Установить Docker Engine, Compose plugin, Git и Certbot. Открыть firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Не открывать `5432`, `6379`, `5672`, `8000`, `8001`, `8002` и RabbitMQ management port.

## 6. TLS certificate

До запуска production nginx получить certificate. Порт 80 должен быть свободен, DNS уже должен вести на VPS:

```bash
sudo certbot certonly --standalone \
  --preferred-challenges http \
  -d example.com \
  -d www.example.com \
  --email admin@example.com \
  --agree-tos \
  --no-eff-email
```

Compose монтирует `/etc/letsencrypt` read-only. Nginx читает:

```text
/etc/letsencrypt/live/${DOMAIN}/fullchain.pem
/etc/letsencrypt/live/${DOMAIN}/privkey.pem
```

Для renewal в standalone mode nginx нужно кратко остановить:

```bash
sudo certbot renew \
  --pre-hook "docker compose --project-directory /opt/koleso/backend --env-file /opt/koleso/backend/.env.production -f /opt/koleso/backend/compose.production.yml stop nginx" \
  --post-hook "docker compose --project-directory /opt/koleso/backend --env-file /opt/koleso/backend/.env.production -f /opt/koleso/backend/compose.production.yml start nginx"
```

Проверить renewal dry run до включения timer.

## 7. Production environment

На VPS:

```bash
cd /opt/koleso/backend
cp .env.production.example .env.production
chmod 600 .env.production
```

Заменить все `example.com`, `change-me` и Timeweb connection values. Сгенерировать разные Django secrets и random passwords для Redis/RabbitMQ.

Frontend production URLs уже same-origin:

```env
VITE_API_URL=/api
VITE_RECOMMENDER_URL=/api/v1
VITE_ASSISTANT_URL=/api/assistant
```

Проверить configuration без запуска:

```bash
docker compose \
  --env-file .env.production \
  -f compose.production.yml \
  config --quiet
```

## 8. Build and start

```bash
cd /opt/koleso/backend
docker compose \
  --env-file .env.production \
  -f compose.production.yml \
  up -d --build
```

`main_service` автоматически запускает Django migrations и `collectstatic`. `recommender_api` запускает Alembic migration. Assistant запускает свои Django migrations.

Проверить:

```bash
docker compose --env-file .env.production -f compose.production.yml ps
docker compose --env-file .env.production -f compose.production.yml logs --tail=200
curl -I http://example.com
curl -fsS https://example.com/health/
curl -fsS https://example.com/api/excursions/
curl -fsS "https://example.com/api/v1/recommendations/?session_id=smoke&limit=3"
curl -fsS https://example.com/nginx-health
```

Assistant smoke:

```bash
curl -fsS https://example.com/api/assistant/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Привет"}'
```

Создать Django superuser:

```bash
docker compose \
  --env-file .env.production \
  -f compose.production.yml \
  exec main_service python manage.py createsuperuser
```

## 9. SMTP smoke

```bash
docker compose \
  --env-file .env.production \
  -f compose.production.yml \
  exec main_service \
  python manage.py shell -c \
  "from django.core.mail import send_mail; send_mail('Koleso SMTP test','SMTP works',None,['recipient@example.com'],fail_silently=False)"
```

Проверить доставку, spam folder, SPF, DKIM и DMARC.

## 10. Persistent data and backup

Named volumes:

- `django_media` — user uploads;
- `django_static` — collected Django static;
- `redis_data`;
- `rabbitmq_data`;
- `celery_beat_data`;
- `recommender_models`;
- `assistant_chroma_data`;
- `huggingface_cache`.

DB backup настраивается в Timeweb DBaaS. Отдельно нужен регулярный backup `django_media` и Chroma volume. Redis/Celery cache можно восстановить, RabbitMQ durable state желательно сохранять.

Никогда не использовать `docker compose down -v` на production без отдельного подтверждения и backup.

## 11. Update and rollback

Update:

```bash
git pull --ff-only
docker compose --env-file .env.production -f backend/compose.production.yml build
docker compose --env-file .env.production -f backend/compose.production.yml up -d
```

Перед update сохранить текущий commit SHA. Rollback: вернуть предыдущий release commit/tag, пересобрать и выполнить `up -d`. Database migrations должны иметь проверенный backward strategy; автоматический downgrade не выполнять.

## External blockers before real deploy

- точный domain и DNS;
- VPS SSH access;
- Timeweb DBaaS host, port, user, password и CA certificate;
- `pgvector` enabled;
- Timeweb mailbox и SMTP password;
- Yandex API key/folder;
- Let's Encrypt certificate;
- production OAuth credentials, если social login остаётся включён;
- backup retention decision;
- финальный RAM замер.

## Official Timeweb references

- [PostgreSQL connection and TLS](https://timeweb.cloud/docs/dbaas/postgresql/connect-to-database)
- [PostgreSQL extensions and pgvector](https://timeweb.cloud/docs/dbaas/postgresql/extensions)
- [Timeweb mail](https://timeweb.cloud/docs/mail)
- [SMTP settings](https://timeweb.cloud/docs/mail/email-clients-configuration)
- [DNS records](https://timeweb.cloud/docs/domains/dns-records-management)
