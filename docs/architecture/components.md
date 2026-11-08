# Architecture: component map

- Last verified: 2026-11-08
- Evidence: `ast-index.cmd search`, route/config source files
- Owner: agent

| Component | Entry points | Owns | Key neighbours |
| --- | --- | --- | --- |
| Frontend | `frontend/src/main.tsx`, `router/index.tsx` | pages, layout, browser auth state, API calls | main API, recommender, assistant |
| Main service | `backend/main_service/config/urls.py` | excursions, accounts, orders, reviews, wishlist, analytics, Django Admin | PostgreSQL, Redis, RabbitMQ |
| Recommender | `backend/recommendation_service/main.py` | recommendation/similar API, training, cache, consumer | PostgreSQL/pgvector, Redis, RabbitMQ, main service internal API |
| Assistant | `backend/assistant_service/config/urls.py` | `/v1/chat/`, RAG, chat storage | PostgreSQL, Redis, Chroma volume, LLM provider |
| Vectorizer | `backend/vectorizer/celery_app.py` | asynchronous vectorisation queue | RabbitMQ, Redis, Chroma volume, LLM provider |

Frontend route inventory is in `frontend/src/router/index.tsx`. It has public
catalogue/content routes and protected booking/account routes. This is current
code behaviour; it may differ from product intent and must be treated as a
separate implementation task.

Main-service domain apps:

| App | Main concepts |
| --- | --- |
| `accounts` | custom email-based user, profile, JWT/social auth, verification |
| `excursions` | category, excursion, image, slot, programme day, ticket type |
| `bookings` | tour order, contact method and lifecycle status |
| `reviews` | moderated review and review images |
| `wishlist` | user/excursion saved relation |
| `analytics` | excursion view events and internal recommendation feeds |

`frontend/public/` stores logo, hero/certificate images, social icons and two
legal DOCX downloads. Binary files are published assets, not documentation.
