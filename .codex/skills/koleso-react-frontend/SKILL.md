---
name: koleso-react-frontend
description: Build, redesign, review, or refactor the Koleso 55 React/Vite frontend. Use for tasks involving frontend pages, React components, routing, API integration, TanStack Query, auth/session handling, business-rule display, responsive UX, accessibility, and the project design system inspired by travelsnob.ru, manawa.com, and frontend/public/hero-bg.jpg.
---

# Koleso React Frontend

Use this skill for any `frontend/` task.

## Required Context

Read before editing:

- `AGENTS.md`
- `docs/FRONTEND_DESIGN_SYSTEM.md`
- `docs/BACKEND_INTEGRATION_PLAN.md`
- `frontend/src/types/index.ts`
- affected files in `frontend/src/api`, `frontend/src/pages`, `frontend/src/components`

Use `ast-index` first:

```powershell
ast-index.cmd update
ast-index.cmd search "ComponentName" --module frontend
ast-index.cmd refs "SymbolName"
```

## Product Goal

Build modern travel UX for "Колесо путешествий 55":

- premium editorial first, closer to `travelsnob.ru`;
- use `manawa.com` for catalog usability patterns only;
- clear excursion discovery, booking, payment, account, certificates, reviews, recommendations;
- show everything backend exposes;
- never hide business rules that affect booking, payment, cancellation, slots, auth, reviews, favorites.

## Design System

Use tokens from `docs/FRONTEND_DESIGN_SYSTEM.md`.

Core palette from `frontend/public/hero-bg.jpg`:

- travel blue: `#0B8ED8`
- deep brand blue: `#0A3F9A`
- sky mist: `#D9EEF7`
- river green: `#6FA36B`
- museum cream: `#F4EFE6`
- brick accent: `#9B4A31`
- ink: `#172033`
- surface: `#FFFFFF`

Do not create one-hue blue-only UI. Use green, cream, brick, and neutral accents for depth.

## UI Rules

- First screen must be usable product UI, not marketing-only splash.
- Homepage may have hero, but catalog/account/booking must be task-first.
- Use real photos/assets. Do not use decorative gradient blobs/orbs.
- Cards: radius max `8px` unless existing component needs different.
- No card inside card.
- Use stable aspect ratios for excursion cards: image `3/4`.
- All states required: loading, error, empty, success, disabled.
- Mobile and desktop must both fit text without overlap.
- Use icons for common actions when icon library exists; otherwise keep buttons text clear.

## API Rules

Django API goes through `frontend/src/api/axios.ts`.

Recommender API currently returns objects:

- `GET /api/v1/recommendations/user/{user_id}` -> `{ recommendations, user_id, session_id, algorithm_used }`
- `GET /api/v1/recommendations/` -> `{ recommendations, user_id, session_id, algorithm_used }`
- `GET /api/v1/similar/{excursion_id}` -> `{ similar_excursions, excursion_id, algorithm_used }`

Frontend functions must unwrap arrays before returning to pages.

For same-origin deploy behind nginx:

- `VITE_API_URL=/api`
- `VITE_RECOMMENDER_URL=/api/v1`

## Business Coverage

Before building a page, inspect backend serializers/views/models for real fields and rules.

Must expose:

- guest booking with optional auth;
- excursion categories, prices, duration, slots, availability, ratings, reviews, images;
- price model: per person by default, adult/child split when backend supports it, negotiated/custom fallback when price is not fixed;
- trusted price and payment amount come from backend only;
- booking status: `new`, `confirmed`, `paid`, `cancelled`, `completed`;
- YooKassa test payment as main post-booking path;
- manager fallback for negotiated/custom price or online payment issues;
- guest order access link when backend supports it;
- slot occupied only after successful payment;
- cancellation allowed only more than 48h before event; otherwise show refund request instructions;
- auth-required account pages;
- favorites and recommendations;
- payment status and YooKassa test-mode redirect when implemented;
- email verification warning if backend returns it;
- legal consent checkboxes on registration and guest booking.

## MVP Priority

1. Public UI kit page at `/ui-kit`.
2. Homepage.
3. Booking/order page.
4. Legal pages and consent UI.
5. Frontend/backend contract fixes.

Later:

- QA/FAQ.
- Gift certificates.
- Recommendation system explanation.
- About.
- Blog.

## Workflow

1. Identify route/page/component/API touched.
2. Use `ast-index` for symbol map.
3. Read backend contract if UI depends on data shape.
4. Update types first, then API wrapper, then page/component.
5. Apply design tokens, not ad hoc colors.
6. Add loading/error/empty states.
7. Run:

```powershell
cd frontend
npm run lint
npm run build
```

If local app is changed visually, run browser check at desktop and mobile viewport.

## When Unsure

Ask only for product decisions:

- exact copy tone;
- payment/legal policy;
- whether a backend field should be public;
- priority between reference-site aesthetics and existing implementation constraints.
