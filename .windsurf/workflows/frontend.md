---
description: frontend
---

Create and maintain the production-ready frontend for "Колесо путешествий 55".

## Required Project Context

- Follow `AGENTS.md`.
- Follow `docs/FRONTEND_DESIGN_SYSTEM.md`.
- Use `.codex/skills/koleso-react-frontend/SKILL.md` as React/frontend workflow.
- Backend integration plan: `docs/BACKEND_INTEGRATION_PLAN.md`.

## Tech Stack

- React + TypeScript + Vite
- React Router
- Tailwind CSS
- Axios + TanStack Query
- React Hook Form + Zod where forms are complex
- Framer Motion and Swiper only where they improve UX
- Context API for auth/session
- JWT with refresh token

## Visual Direction

- Modern travel marketplace.
- References: `travelsnob.ru`, `manawa.com`.
- Use color tokens from `frontend/public/hero-bg.jpg`:
  - `#0B8ED8`, `#0A3F9A`, `#D9EEF7`, `#6FA36B`, `#F4EFE6`, `#9B4A31`, `#172033`.
- Use real imagery. Avoid decorative blobs/orbs.
- Cards max 8px radius.
- No nested cards.

## Backend Coverage

Show everything user-facing from backend:

- excursions, categories, slots, prices, duration, location, images;
- bookings and statuses;
- reviews;
- wishlist;
- account/profile;
- recommendations/similar excursions;
- analytics tracking where required;
- payment state when YooKassa test mode is implemented.

## API Contract

Django:

```env
VITE_API_URL=/api
```

Recommender:

```env
VITE_RECOMMENDER_URL=/api/v1
```

Local dev may use:

```env
VITE_API_URL=http://localhost:8001/api
VITE_RECOMMENDER_URL=http://localhost:8002/api/v1
```

Recommender responses are objects, not arrays. Unwrap:

- `data.recommendations`
- `data.similar_excursions`

## Required Pages

- Home
- Catalog
- Excursion detail
- Booking
- Account
- Login/Register/Password reset/OAuth callback
- Certificates
- News/Events
- Recommendation info
- Payment return page after YooKassa test redirect

## Required States

Every API-driven view needs:

- loading
- error
- empty
- success
- disabled/submitting
- auth-required where relevant

## Checks

```powershell
cd frontend
npm run lint
npm run build
```
