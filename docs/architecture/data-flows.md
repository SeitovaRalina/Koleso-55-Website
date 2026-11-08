# Architecture: key data flows

- Last verified: 2026-11-08
- Evidence: URL modules, models and API client source
- Owner: agent

## Catalogue

Browser → frontend `excursionsApi` → Django `/api/excursions/` → excursion,
category and slot data. Images are served as media/static assets. Filtering is
implemented server-side through `excursions` views/filters.

## Authentication and account

Browser → frontend `authApi` → Django accounts API → `CustomUser`. JWT access
token is attached by `frontend/src/api/axios.ts`; its refresh path is handled
by the axios response interceptor. Registration/login/profile/email flows are
listed in `api/contracts.md`.

## Booking

Browser → `bookingsApi.createOrder` → `/api/bookings/orders/` → `TourOrder`
with an excursion, slot, contact details, participant count and status. Django
Admin manages orders. Order status `paid` changes slot booked count in model
logic; payment gateway implementation requires separate verification.

Current code has a documented gap: router wraps booking page in
`ProtectedRoute`, while product rules say guest booking is allowed. This is an
open product/code discrepancy, not silently corrected by documentation.

## Recommendations and analytics

Frontend records view events through Django analytics API. Main service exposes
internal excursion/popularity feeds. Recommender consumes RabbitMQ, maintains
its own data/caches and exposes `/api/v1/recommendations` and `/api/v1/similar`.
Frontend unwraps `recommendations` / `similar_excursions` response fields.

## Assistant and vectorisation

Frontend assistant client calls assistant service through production nginx
prefix `/api/assistant/`. Assistant uses RAG/chat storage and Chroma data.
Vectorizer worker consumes its dedicated queue and shares Chroma persistence.
Do not assume either service is enabled in a given environment; verify health.
