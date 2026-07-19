# Timeweb Nginx Deploy

Цель: подготовить один Timeweb service/VPS для frontend + backend через Docker Compose и nginx reverse proxy.

## Public routes

- `/` - frontend static files.
- `/api/*` - Django `main_service`.
- `/admin/*` - Django admin.
- `/health/` - Django health.
- `/api/v1/*` - FastAPI `recommendation_service`.
- `/media/*` - Django media.
- `/static/*` - Django static.

## Production env checklist

Domain is not ready yet. Replace `example.com` after domain purchase/connection.

```env
DEBUG=False
SECRET_KEY=change-me
ALLOWED_HOSTS=example.com,www.example.com,main-service
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
CORS_ORIGINS=https://example.com,https://www.example.com
DOMAIN=example.com
PROTOCOL=https

RECOMMENDER_BASE_URL=http://recommender_api:8000
DJANGO_BASE_URL=http://main-service:8000

YOOKASSA_SHOP_ID=change-me
YOOKASSA_SECRET_KEY=change-me
YOOKASSA_RETURN_URL=https://example.com/payment/return
YOOKASSA_WEBHOOK_SECRET=change-me
```

Frontend production env for same-origin deploy:

```env
VITE_API_URL=/api
VITE_RECOMMENDER_URL=/api/v1
```

## Build and run

```powershell
cd backend
docker compose up -d --build postgres redis rabbitmq
docker compose up -d --build main_service recommender_api django_celery_worker django_celery_beat recommender_worker
docker compose --profile proxy up -d nginx
```

## Checks

```powershell
curl http://localhost/health/
curl http://localhost/api/schema/
curl http://localhost/api/v1/recommendations/?session_id=test&limit=3
```

## HTTPS

Use one of:

- Timeweb panel SSL termination before VPS.
- certbot on host with mounted certs into `backend/nginx/ssl`.
- external CDN/proxy with HTTPS and origin HTTP.

Decision pending: choose HTTPS method after domain is known.

If nginx terminates TLS itself, add cert files:

```text
backend/nginx/ssl/fullchain.pem
backend/nginx/ssl/privkey.pem
```

Then enable `listen 443 ssl` block in nginx config.

## Production hardening

- Remove `ALLOWED_HOSTS=*`.
- Disable `debug_toolbar` in production or conditionally include only when `DEBUG=True`.
- Use gunicorn/uvicorn workers instead of Django `runserver`.
- Add persistent volumes for media/static if serving user files.
- Add backup policy for Postgres volume.
- Log nginx access/error to files or Docker logs.
- Restrict RabbitMQ management port in production.

## Frontend deploy

Chosen target: same VPS/nginx.

1. Build frontend:

```powershell
cd frontend
npm ci
npm run build
```

2. Mount `frontend/dist` to nginx `/usr/share/nginx/html`.

Separate static hosting is not current target.

## Rollback

```powershell
cd backend
docker compose ps
docker compose logs --tail=200 main_service recommender_api nginx
docker compose restart main_service recommender_api nginx
```
