# Architecture: system context

- Last verified: 2026-11-08
- Evidence: `backend/docker-compose.yml`, `backend/compose.production.yml`
- Owner: agent

```text
Visitors / administrators
           |
      React frontend
           |
         nginx
   ________|______________________________
   |              |                       |
Django         FastAPI                 assistant
main_service   recommender              service
   |              |                       |
PostgreSQL   PostgreSQL/pgvector      PostgreSQL + Chroma volume
   |              |
Redis / RabbitMQ / Celery workers / vectorizer
```

`main_service` owns customer-facing catalogue, account, Admin and booking
domain. Recommendation, assistant and vectorizer have their own operational
dependencies; their availability must not be assumed from frontend behaviour.
Production hostnames, credentials and certificate material are deliberately
outside repository documentation.
