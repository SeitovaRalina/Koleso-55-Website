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

Development nginx routes `/api/` to Django and `/api/v1/` to recommender.
Assistant public mapping is defined in production frontend nginx template, not
in `backend/nginx/nginx.conf`; use the relevant compose profile deliberately.
