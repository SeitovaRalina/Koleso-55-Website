# Jobs, queues and observability

- Last verified: 2026-11-08
- Evidence: Compose files, Celery commands, service entry points
- Owner: agent after runtime evidence

| Process | Responsibility | Health evidence |
| --- | --- | --- |
| Django Celery worker | main-service asynchronous tasks | Celery inspect ping in production compose |
| Django Celery beat | scheduled main-service tasks | process health probe |
| Recommender consumer/worker | RabbitMQ events, model training/cache tasks | API health + Celery ping |
| Vectorizer worker | `vectorizer` queue processing | Celery ping |
| Assistant | RAG/chat process, Chroma volume | `/health/` |

Use container logs and health endpoints for diagnosis; do not paste raw
production logs or user content into reports/docs. Async recommendation failure
must not be reported as successful recommendation output. Verify actual queue
names/configuration before operational changes.
