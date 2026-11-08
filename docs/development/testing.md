# Testing and evidence

- Last verified: 2026-11-08
- Evidence: root `AGENTS.md`, package manifests, existing recommender tests
- Owner: task implementer

| Area | Baseline command | Required when relevant |
| --- | --- | --- |
| Django | `python manage.py check`, `python manage.py test` from `backend/main_service` | model/API/Admin changes |
| Recommender | `pytest`, `alembic upgrade head` from `backend/recommendation_service` | recommender API/model changes |
| Frontend | `npm run lint`, `npm run build` from `frontend` | TypeScript/UI/API-client changes |
| UI | browser desktop + mobile checks | visual/interaction change |
| E2E | real task scenario with safe local data | cross-service flow |

Run smallest sufficient checks, then expand by risk. Exact command, result and
unverified areas go in testing report when required by `reports/README.md`.
Documentation-only/low-risk work still validates paths/links, but does not need
runtime E2E or testing/review report unless risk/user/merge requires one.
