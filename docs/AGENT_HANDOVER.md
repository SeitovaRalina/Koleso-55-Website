# Agent handover — production state

Updated: 2026-10-24. Read this file before making production changes.

## Scope and hard boundaries

- Production domain: `https://koleso-travel55.ru`.
- Timeweb VPS public IP: `201.24.50.190`; VPS private IP: `192.168.0.4`.
- Timeweb PostgreSQL DBaaS is private-only at `192.168.0.5` on
  `192.168.0.0/24`. Do not expose a public database IP just to add TLS.
- Production checkout: `/opt/koleso`.
- SSH account: `root`; local key is `C:\Users\seito\.ssh\koleso_timeweb`.
- Never stop, restart, reconfigure, or inspect secrets of
  `candidate-screening-bot.service`. It is an unrelated Telegram AI bot.
- Never print or commit production `.env` values. Use examples and redact
  passwords, tokens, client secrets, and private keys.

## Production command

```bash
cd /opt/koleso
docker compose --env-file backend/.env.production \
  -f backend/compose.production.yml <command>
```

The production source of truth is `main`. Before deploying, make a DB/media
backup and confirm the exact release commit. Do not use `docker compose down
-v` in production.

## Current capacity and safe runtime

The VPS has **2 GiB RAM**. Timeweb OOM-killer previously killed Docker and
made SSH unavailable. A persistent 4 GiB swap file is enabled. Swap reduces
the chance of an outage; it is not a substitute for RAM for ML workloads.

`backend/compose.production.yml` has service memory limits. Docker is enabled
at boot. These services are intentionally running and restart automatically:

- `redis`, `rabbitmq`, `main_service`, `django_celery_worker`,
  `django_celery_beat`, `recommender_api`, `assistant_service`, `nginx`.

These are intentionally stopped with restart policy `no`:

- `recommender_worker`;
- `vectorizer_worker`.

Starting all Compose services on this VPS can cause another OOM incident.
Do **not** run a blanket `docker compose up -d --build --wait` until RAM is
increased and the full stack has been measured. Build/recreate only required
services, then check `docker stats --no-stream` and `free -h`.

There is also a historical `Dead` vectorizer container. Attempts to remove or
recreate it previously blocked in Docker. It does not affect public routes.
Do not restart Docker or reboot solely to remove it while the website is live;
schedule a maintenance window, confirm backups, then clean it up.

## Verified routes and service behaviour

- `GET /health/` — Django health.
- `GET /admin/` — Django Admin; unauthenticated result is `302`.
- `GET /static/admin/css/base.css` — confirms admin static files.
- `GET /api/assistant/health/` — assistant health.
- `GET /api/v1/recommendations/?session_id=healthcheck` — recommender smoke.
- `GET /api/v1/health` is expected to be `404`; FastAPI health is internal at
  `http://recommender_api:8000/health`.

Nginx requires DNS names for both `recommender_api` and `assistant_service`
when it starts. Start these APIs before recreating nginx, or nginx will fail
with `host not found in upstream`.

## Incident fixes already deployed

1. Static files: Django collects to `/app/staticfiles`; production volume is
   mounted to that path and nginx serves it as `/static/`.
2. Admin saves: recommendation event enqueue failures are logged, not allowed
   to turn a successful Django Admin save into HTTP 500.
3. RabbitMQ: Celery accepts an AMQP URL ending in `//` for default vhost, but
   Pika reads it as empty. `analytics.tasks` normalises an empty Pika vhost to
   `/`. The full Django → Celery → RabbitMQ → recommender path was smoke-tested.
4. OAuth: Google uses production credentials from `backend/.env.production`.
   VK is configured but deliberately hidden by `VK_AUTH_ENABLED=False` /
   `VITE_VK_AUTH_ENABLED=false`; do not enable it until VK OAuth is configured.
5. Password reset emails point to the frontend route
   `/password-reset/<uid>/<token>` rather than a JSON-only API page.

## Known functional gap

The former “Остались вопросы?” form on the excursion page had no submit
handler, API endpoint, database model, email, or admin workflow; submitted
text was lost. KOLE-3 replaces it with a contacts link. An inquiry form can
return only after its model/API/admin workflow and manager notification exist.

## Smoke procedure

```bash
cd /opt/koleso
docker compose --env-file backend/.env.production \
  -f backend/compose.production.yml ps
docker stats --no-stream
free -h
curl -fsS https://koleso-travel55.ru/health/
curl -fsS https://koleso-travel55.ru/api/assistant/health/
curl -fsS 'https://koleso-travel55.ru/api/v1/recommendations/?session_id=smoke'
systemctl is-active candidate-screening-bot.service
```

Check `admin` in a browser after deployment. Its first cold request can be
slow; repeated unauthenticated requests returned `302` in about 0.1 seconds.

## Repository workflow

- Read `AGENTS.md`, this handover, and relevant docs before changing code.
- Use `ast-index` before code search and `caveman` for responses.
- Make no production mutation without a concise commentary update.
- Keep runtime credentials out of Git. Update `.env.example` when variables
  change.
- Run focused checks after each code change. Required baseline checks:
  `python manage.py check`, recommender `pytest`, and frontend `npm run lint`
  plus `npm run build` when the affected dependencies are available.
- Use Conventional Commits and keep commits logically scoped.
