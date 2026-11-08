# HTTP contracts

- Last verified: 2026-11-08
- Evidence: service URL/router files and frontend API modules
- Owner: agent

## Main service

Base in frontend: `VITE_API_URL` or `http://localhost:8001/api`.

| Area | Routes | Source |
| --- | --- | --- |
| Health/Admin/schema | `/health/`, `/admin/`, `/api/schema/`, `/api/docs/`, `/api/redoc/` | `config/urls.py` |
| Excursions | `GET /api/excursions/`, `GET /api/excursions/<pk>/`, categories, max-price | `excursions/urls.py` |
| Accounts | register, login, refresh, logout, password reset, email verify, profile, Google/VK config/login | `accounts/urls.py` |
| Bookings | create order; authenticated own order list/detail/cancel | `bookings/urls.py` |
| Reviews | per-excursion list, homepage, own reviews, create/update | `reviews/urls.py` |
| Wishlist | list, add, delete, check | `wishlist/urls.py` |
| Analytics | view start/heartbeat/end; recommendation proxies; internal feeds | `analytics/urls.py` |

Exact serializers and filters remain in source/live schema. Known client/server
contract question: frontend contains `getSlots()` for
`/excursions/<id>/slots/`, but current `excursions/urls.py` does not declare
that route. Treat as a defect investigation, not a supported contract.

## Recommendation service

Base in frontend: `VITE_RECOMMENDER_URL` or `http://localhost:8002/api/v1`.

| Route | Meaning | Response field used by frontend |
| --- | --- | --- |
| `GET /health` | dependency/model readiness | health payload |
| `GET /api/v1/recommendations/user/{user_id}` | personalized recommendations | `recommendations` |
| `GET /api/v1/recommendations/` | user or session recommendations | `recommendations` |
| `GET /api/v1/similar/{excursion_id}` | content-based similar excursions | `similar_excursions` |
| `/api/v1/admin/*` | retrain/cache/statistics maintenance | internal only in production proxy |

Query names differ: user-specific endpoint uses `top_k`; generic endpoint uses
`limit`. The frontend client reflects this distinction.

## Assistant service

| Route | Meaning |
| --- | --- |
| `GET /health/` | assistant health |
| `POST /v1/chat/` | chat/RAG request |
| `GET /ui/` | service-local chat template |

Production nginx maps public `/api/assistant/` to assistant `/v1/` and applies
rate limiting. Verify method/payload against `assistant/api/serializers.py`
before any client change.
