# Local stack

- Last verified: 2026-11-08
- Evidence: `backend/docker-compose.yml`, `backend/nginx/nginx.conf`
- Owner: agent

`backend/docker-compose.yml` defines development containers:

| Group | Services |
| --- | --- |
| Data/broker | Postgres, Redis, RabbitMQ |
| Main domain | main service, Django Celery worker, Django Celery beat |
| Recommendation | recommender API, recommender worker |
| Assistant | assistant service, vectorizer worker |
| Proxy | nginx, optional `proxy` profile |

Main service health: `/health/`; recommender health: `/health`; assistant
health: `/health/`. Container health means process/dependency probe succeeded,
not that all product flows were E2E tested.

## Browser development URL

Run the frontend at `http://127.0.0.1:4173`. It is the single browser origin
for local product checks: Vite proxies `/api/` and `/media/` to Django at
`127.0.0.1:8001`, `/api/v1/` to recommender at `127.0.0.1:8002`, and
`/api/assistant/` to assistant at `127.0.0.1:8000` (rewritten to `/v1/`). Do
not open service ports in the browser for normal E2E checks. This avoids a
separate browser origin and CORS configuration.

For a same-origin assistant smoke check use `/api/assistant/health/`; Vite
forwards it to the service's `/health/`. Recommender health remains service
route `/health`; for a browser smoke check, Vite exposes it as
`/api/v1/health`.

Development nginx routes `/api/` to Django and `/api/v1/` to recommender.
Assistant public mapping is defined in production frontend nginx template, not
in `backend/nginx/nginx.conf`; use the relevant compose profile deliberately.
