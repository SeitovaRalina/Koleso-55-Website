# Release review: PR 19

- Status: approved_for_merge
- Date: 2026-11-10
- PR: https://github.com/SeitovaRalina/Koleso-55-Website/pull/19
- Base: `main`
- Head: `fix/slots-about-footer`

## Independent scope check

Reviewed all application changes in the PR: request ownership and
verified-email claiming, Django migrations/Admin, slot end calculation,
catalogue pagination and sidebars, form prefill, About/footer routes, local
same-origin API routing, harness and durable documentation. No unapproved
production behaviour was found after the user-approved plan revisions.

## Findings closed during review

| ID | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| REL-001 | P1 | Automatic slot-end calculation raised `TypeError` when `Slot.time` was a string. | Normalize date/time with Django field conversion; add regression test. |
| REL-002 | P2 | Unified request TypeScript status union omitted Django inquiry state `closed`. | Add `closed` to `UnifiedRequest` contract. |
| REL-003 | P2 | Catalogue test mock matched Vite modules under `src/api/` and returned JSON in place of JavaScript. | Limit mock interception to browser HTTP requests under `/api/`. |

## Verification evidence

- `python manage.py check` — pass.
- `python manage.py makemigrations --check --dry-run` — pass.
- Changed backend scope: `accounts`, `bookings`, `excursions` — 51 Django
  tests pass.
- Frontend: lint and production build pass; Vite reports only its existing
  >500 kB chunk advisory.
- Catalogue Playwright suite — 8 pass.
- Live form-prefill and account-request Playwright suite — 4 pass against
  local Docker services.
- Local service health: Django, recommender and assistant return HTTP 200;
  recommender async dependencies import successfully.
- Live catalogue test data verified three pages: 25 active records as 12/12/1.

## Known non-blocker

The unrelated full `reviews` suite waits for an external toxicity-model
download in the local environment. It is outside this PR's changed scope;
do not treat the timeout as a passing result. The affected code paths above
have dedicated passing coverage.

## Release decision

Safe to merge after GitHub reflects the pushed review-fix commit. Deploy only
through the documented production preflight: backup, capacity and health
checks, migrations, targeted service recreation and browser/Admin smoke.
